# --- Stage 1: Build Frontend ---
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Final Image ---
FROM node:18-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install backend dependencies
COPY package*.json ./
RUN npm install --production

# ── CACHE BUSTER ──────────
# Bump this to force rebuild of the layers below
ARG CACHEBUST=2026-03-02.4
RUN echo "Cache bust: $CACHEBUST"
# ──────────────────────────

# Copy backend source
COPY api/ ./api/
COPY models/ ./models/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Pre-download Xenova/all-MiniLM-L6-v2 at BUILD time.
ENV XENOVA_CACHE_DIR=/app/.cache/xenova
RUN node -e "\
import('@xenova/transformers').then(async ({ pipeline, env }) => {\
  env.cacheDir = '/app/.cache/xenova';\
  console.log('Downloading Xenova/all-MiniLM-L6-v2 ...');\
  const p = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');\
  const t = await p('warmup', { pooling: 'mean', normalize: true });\
  console.log('Model ready — dimension:', t.data.length);\
  process.exit(0);\
}).catch(e => { console.error(e.message); process.exit(1); });"

# Hugging Face Spaces environment
EXPOSE 7860
ENV PORT=7860
ENV NODE_ENV=production

# Start the Node.js API
CMD ["node", "api/app.js"]
