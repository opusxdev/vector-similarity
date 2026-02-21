
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










# v3 
FROM python:3.11-slim as python-base

WORKDIR /app/python
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Download the embedding model at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Node.js stage
FROM node:18-slim

# Install Python runtime + curl (needed for health check)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies and model cache from python-base
COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-base /root/.cache /root/.cache
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

# Copy package.json and install Node.js dependencies
COPY package*.json ./
RUN npm install --production

# Copy application files
COPY api/app.js ./api/
COPY api/embedding_service.py ./api/
COPY models/ ./models/
COPY frontend/dist ./frontend/dist

# Only copy .env if it exists
COPY .env* ./

EXPOSE 7860 8001

# Improved start script with better error handling
RUN cat > /app/start.sh << 'SCRIPT'
#!/bin/bash
set -e

echo "Starting embedding service in background..."
python3 api/embedding_service.py &
EMBED_PID=$!

echo "Waiting for embedding service to be ready..."
for i in {1..30}; do
  if curl -sf http://localhost:8001/health > /dev/null 2>&1; then
    echo "✓ Embedding service ready after $i attempts"
    break
  fi
  
  if [ $i -eq 30 ]; then
    echo "✗ Embedding service failed to start after 30 attempts"
    kill $EMBED_PID 2>/dev/null || true
    exit 1
  fi
  
  echo "  Attempt $i/30 - waiting..."
  sleep 2
done

echo "Starting Node.js API..."
exec node api/app.js
SCRIPT
chmod +x /app/start.sh

CMD ["/app/start.sh"]