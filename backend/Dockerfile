# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libasound2-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libasound2 \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r jarvis && useradd -r -g jarvis jarvis

# Copy only necessary files from builder
COPY --from=builder /root/.local /home/jarvis/.local
COPY . .

# Set permissions
RUN mkdir -p data/db && chown -R jarvis:jarvis /app

# Environment variables
ENV PATH=/home/jarvis/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER jarvis

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
