FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy and install jobextractor requirements
COPY jobextractor/requirements.txt jobextractor_requirements.txt
RUN pip install --no-cache-dir -r jobextractor_requirements.txt

# Copy and install backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY jobextractor/ ./jobextractor/
COPY backend/ ./backend/

# Set working directory to backend
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
