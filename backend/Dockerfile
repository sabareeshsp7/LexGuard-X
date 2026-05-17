# ─────────────────────────────────────────────
#  LexiWare Backend — Production Dockerfile
#  Deploys to Google Cloud Run
# ─────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install system-level build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create runtime directories
RUN mkdir -p /app/uploads /app/chroma_db

# Cloud Run injects PORT env var (default 8080)
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
