# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY apps/worker/requirements.txt worker_requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r worker_requirements.txt

COPY apps/api/requirements.txt api_requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r api_requirements.txt

# Stage 2: Final
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies and curl for healthcheck
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY libs/ ./libs/
COPY apps/worker/ ./apps/worker/
COPY apps/api/ ./apps/api/
COPY .env .env

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

WORKDIR /app/apps/api

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/api/health/ready || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
