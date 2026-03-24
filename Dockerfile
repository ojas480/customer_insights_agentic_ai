FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements entirely
COPY requirements.txt .

# Install dependencies (ignoring faiss-cpu issues by ensuring we use pure python or simple compiled wheels)
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data /app/data/faiss_index

# Copy all source code
COPY . .

# Generate the dataset and FAISS index during the build
RUN python -m scraper.download_reviews
RUN python -m rag.build_index

# Expose the API port
EXPOSE 8000

# Start FastAPI using the dynamic $PORT provided by Render, falling back to 8000
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
