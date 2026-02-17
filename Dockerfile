# FROM python:3.10-slim

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# ENV TRANSFORMERS_CACHE=/app/.cache
# ENV HF_HOME=/app/.cache

# WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 7860

# CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "7860"]





# FROM python:3.10-slim

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# ENV TRANSFORMERS_CACHE=/app/.cache
# ENV HF_HOME=/app/.cache

# WORKDIR /app

# # Install system dependencies including Node.js
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     git \
#     curl \
#     && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
#     && apt-get install -y nodejs \
#     && rm -rf /var/lib/apt/lists/*

# # Install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy all application files
# COPY . .

# # Build React frontend
# WORKDIR /app/frontend
# RUN npm install
# RUN npm run build

# # Return to app directory
# WORKDIR /app

# EXPOSE 7860

# CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "7860"]




# dev 3 new 

# Multi-stage Dockerfile for Node.js + Python hybrid setup

FROM python:3.11-slim as python-base

# Install Python dependencies for embedding service
WORKDIR /app/python
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Download the embedding model at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Node.js stage
FROM node:18-slim

# Install Python runtime
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies and model cache from python-base
COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-base /root/.cache /root/.cache

# Copy Python requirements and install
# COPY requirements.txt .
# RUN pip3 install --no-cache-dir -r requirements.txt

# Copy package.json and install Node.js dependencies
COPY package*.json ./
RUN npm install --production

# Copy application files
COPY api/app.js ./api/
COPY api/embedding_service.py ./api/
COPY models/ ./models/
COPY frontend/dist ./frontend/dist

# Copy any other necessary files
COPY .env* ./

# Expose ports
# 7860 - Main Node.js API
# 8001 - Python Embedding Service
EXPOSE 7860 8001

# Create startup script
RUN echo '#!/bin/bash\n\
python3 api/embedding_service.py &\n\
sleep 3\n\
node api/app.js\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start both services
CMD ["/app/start.sh"]