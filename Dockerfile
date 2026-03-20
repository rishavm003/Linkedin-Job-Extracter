FROM python:3.11-slim

WORKDIR /app

# System deps for Playwright + psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Download spaCy model
RUN python -m spacy download en_core_web_sm

COPY . .

# Default: run pipeline once
CMD ["python", "main.py", "run"]
