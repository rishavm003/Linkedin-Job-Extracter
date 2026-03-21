FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY jobextractor/requirements.txt jobextractor_requirements.txt
RUN pip install --no-cache-dir -r jobextractor_requirements.txt

COPY backend/requirements.txt backend_requirements.txt
RUN pip install --no-cache-dir -r backend_requirements.txt

COPY jobextractor/ ./jobextractor/
COPY backend/ ./backend/
COPY .env .env

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/api/health/ready || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", \
     "--port", "8000", "--workers", "2"]
