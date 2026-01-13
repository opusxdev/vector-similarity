FROM python:3.10-slim

# Prevent Python from writing pyc files and buffering logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (needed for sentence-transformers / torch)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (filtered by .dockerignore)
COPY . .

# Expose Hugging Face required port
EXPOSE 7860

# Start FastAPI app
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "7860"]
