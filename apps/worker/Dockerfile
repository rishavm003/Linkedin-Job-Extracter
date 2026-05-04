FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the worker app
COPY apps/worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

RUN playwright install chromium
RUN playwright install-deps chromium

# Copy shared libraries and the worker app
COPY libs/ ./libs/
COPY apps/worker/ ./apps/worker/
COPY .env .env

WORKDIR /app/apps/worker

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "from libs.database.postgres import PostgresStorage; \
  PostgresStorage().get_session()" || exit 1

CMD ["python", "main.py", "schedule", "--hours", "6", "--db"]
