
# # Multi-stage Dockerfile for Node.js + Python hybrid setup

# FROM python:3.11-slim as python-base

# # Install Python dependencies for embedding service
# WORKDIR /app/python
# COPY requirements.txt .
# # RUN pip install --no-cache-dir -r requirements.txt

# RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# # Download the embedding model at build time
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# # Node.js stage
# FROM node:18-slim

# # Install Python runtime
# RUN apt-get update && apt-get install -y \
#     python3 \
#     python3-pip \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Copy Python dependencies and model cache from python-base
# COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# COPY --from=python-base /root/.cache /root/.cache

# # Copy Python requirements and install
# # COPY requirements.txt .
# # RUN pip3 install --no-cache-dir -r requirements.txt

# # Copy package.json and install Node.js dependencies
# COPY package*.json ./
# RUN npm install --production

# # Copy application files
# COPY api/app.js ./api/
# COPY api/embedding_service.py ./api/
# COPY models/ ./models/
# COPY frontend/dist ./frontend/dist

# # Copy any other necessary files
# COPY .env* ./

# # Expose ports
# # 7860 - Main Node.js API
# # 8001 - Python Embedding Service
# EXPOSE 7860 8001

# # Create startup script
# RUN echo '#!/bin/bash\n\
# python3 api/embedding_service.py &\n\
# sleep 3\n\
# node api/app.js\n\
# ' > /app/start.sh && chmod +x /app/start.sh

# # Start both services
# CMD ["/app/start.sh"]




# Multi-stage Dockerfile for Node.js + Python hybrid setup

# FROM python:3.11-slim as python-base

# WORKDIR /app/python
# COPY requirements.txt .
# RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# # Download the embedding model at build time
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# # Node.js stage
# FROM node:18-slim

# # Install Python runtime + curl (needed for health check in start.sh)
# RUN apt-get update && apt-get install -y \
#     python3 \
#     python3-pip \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Copy Python dependencies and model cache from python-base
# COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# COPY --from=python-base /root/.cache /root/.cache
# ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

# # Copy package.json and install Node.js dependencies
# COPY package*.json ./
# RUN npm install --production

# # Copy application files
# COPY api/app.js ./api/
# COPY api/embedding_service.py ./api/
# COPY models/ ./models/
# COPY frontend/dist ./frontend/dist
# COPY .env* ./

# EXPOSE 7860 8001

# # Start script: launch embedding service, wait until it's healthy, then start Node
# RUN printf '#!/bin/bash\nset -e\npython3 api/embedding_service.py &\necho "Waiting for embedding service to be ready..."\nfor i in $(seq 1 30); do\n  if curl -sf http://localhost:8001/health > /dev/null 2>&1; then\n    echo "Embedding service ready after $i attempts"\n    break\n  fi\n  echo "Attempt $i/30..."\n  sleep 2\ndone\necho "Starting Node.js API..."\nexec node api/app.js\n' > /app/start.sh && chmod +x /app/start.sh

# CMD ["/app/start.sh"]










# ── Production image: Node.js only ───────────────────────────────────────────
# Embedding runs in-process via @xenova/transformers (ONNX) — no Python needed.
FROM node:18-slim

# curl kept for the HF Spaces health check endpoint
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Node.js deps (cached layer — only rebuilt when package*.json changes)
COPY package*.json ./
RUN npm install --production

# ── CACHE BUSTER: bump to force HF Spaces to pick up new source code ──────────
# Change the value (e.g. date + build number) before each push when you want
# Docker to bypass its layer cache for all COPY/RUN steps below this line.
ARG CACHEBUST=2026-02-21.3
RUN echo "Cache bust: $CACHEBUST"
# ─────────────────────────────────────────────────────────────────────────────

# Copy application source
COPY api/app.js ./api/
COPY models/ ./models/
COPY frontend/dist ./frontend/dist

# Pre-download Xenova/all-MiniLM-L6-v2 at BUILD time.
# Sets env.localFilesOnly=true at runtime (see app.js) so no outbound
# network calls are ever made when the container is actually running.
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

EXPOSE 7860

CMD ["node", "api/app.js"]
