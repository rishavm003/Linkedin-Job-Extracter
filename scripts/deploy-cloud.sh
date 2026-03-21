#!/bin/bash

# JobExtractor - Production Deployment Script
# Deploys to cloud platforms (Render, Railway, etc.)

set -e

echo "☁️  JobExtractor Cloud Deployment Setup"

# Check for required tools
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git is required"; exit 1; }

# Platform selection
echo "Select deployment platform:"
echo "1) Render (Recommended for beginners)"
echo "2) Railway (Fast, simple)"
echo "3) DigitalOcean App Platform"
echo "4) AWS ECS (Advanced)"
read -p "Enter choice (1-4): " PLATFORM

case $PLATFORM in
    1)
        echo "🚀 Setting up Render deployment..."
        
        # Create render.yaml
        cat > render.yaml << 'EOF'
services:
  - type: web
    name: jobextractor-api
    env: python
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: jobextractor-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: jobextractor-redis
          property: connectionString
      - key: ELASTICSEARCH_URL
        fromService:
          type: elasticsearch
          name: jobextractor-es
          property: url
      - key: ADZUNA_APP_ID
        sync: false
      - key: ADZUNA_APP_KEY
        sync: false
      - key: RAPIDAPI_KEY
        sync: false
      - key: APYHUB_API_KEY
        sync: false

  - type: web
    name: jobextractor-frontend
    env: static
    plan: free
    buildCommand: npm run build
    staticPublishPath: frontend/out
    envVars:
      - key: NEXT_PUBLIC_API_URL
        value: https://jobextractor-api.onrender.com
        sync: false

databases:
  - name: jobextractor-db
    plan: free
    databaseName: jobextractor
    user: jobuser

services:
  - type: redis
    name: jobextractor-redis
    plan: free
    
  - type: elasticsearch
    name: jobextractor-es
    plan: free
EOF
        
        echo "✅ render.yaml created"
        echo "📝 Next steps:"
        echo "   1. Push your code to GitHub"
        echo "   2. Connect your GitHub repo to Render"
        echo "   3. Render will auto-detect render.yaml"
        echo "   4. Add your API keys in Render dashboard"
        echo ""
        echo "🔗 Render Dashboard: https://dashboard.render.com"
        ;;
        
    2)
        echo "🚀 Setting up Railway deployment..."
        
        # Create railway.toml
        cat > railway.toml << 'EOF'
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[services]]
name = "jobextractor-api"
source = "."
[services.variables]
DATABASE_URL = "${{ Postgres.DATABASE_URL }}"
REDIS_URL = "${{ Redis.REDIS_URL }}"
ELASTICSEARCH_URL = "${{ Elasticsearch.URL }}"
[services.health_check]
path = "/health"
port = 8000

[[services]]
name = "jobextractor-frontend"
source = "./frontend"
[services.build]
builder = "NIXPACKS"
[services.variables]
NEXT_PUBLIC_API_URL = "${{ jobextractor-api.RAILWAY_PUBLIC_DOMAIN }}"
EOF
        
        echo "✅ railway.toml created"
        echo "📝 Next steps:"
        echo "   1. Install Railway CLI: npm install -g @railway/cli"
        echo "   2. Login: railway login"
        echo "   3. Deploy: railway up"
        echo "   4. Add environment variables in Railway dashboard"
        echo ""
        echo "🔗 Railway Dashboard: https://railway.app"
        ;;
        
    3)
        echo "🚀 Setting up DigitalOcean App Platform..."
        
        # Create .do/app.yaml
        mkdir -p .do
        cat > .do/app.yaml << 'EOF'
name: jobextractor
services:
- name: api
  source_dir: backend
  github:
    repo: your-username/jobextractor
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  env:
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
  - key: REDIS_URL
    value: ${redis.REDIS_URL}
  - key: ELASTICSEARCH_URL
    value: ${elasticsearch.URL}
  http_port: 8000
  routes:
  - path: /api
- name: frontend
  source_dir: frontend
  github:
    repo: your-username/jobextractor
    branch: main
  build_command: npm run build
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  env:
  - key: NEXT_PUBLIC_API_URL
    value: ${api.URL}
  http_port: 3000
  routes:
  - path: /
databases:
- name: db
  engine: PG
  version: "16"
- name: redis
  engine: REDIS
  version: "7"
- name: elasticsearch
  engine: ELASTICSEARCH
  version: "8.11"
EOF
        
        echo "✅ .do/app.yaml created"
        echo "📝 Next steps:"
        echo "   1. Push code to GitHub"
        echo "   2. Connect repo to DigitalOcean App Platform"
        echo "   3. Deploy will start automatically"
        echo ""
        echo "🔗 DigitalOcean: https://cloud.digitalocean.com/apps"
        ;;
        
    4)
        echo "🚀 Setting up AWS ECS deployment..."
        
        # Create ECS deployment files
        mkdir -p aws-deployment
        
        cat > aws-deployment/Dockerfile.prod << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
        
        cat > aws-deployment/task-definition.json << 'EOF'
{
  "family": "jobextractor",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "jobextractor-api",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/jobextractor:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "YOUR_DB_URL"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/jobextractor",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
EOF
        
        echo "✅ AWS deployment files created in aws-deployment/"
        echo "📝 Next steps:"
        echo "   1. Create ECR repository"
        echo "   2. Build and push Docker image"
        echo "   3. Create ECS cluster and task definition"
        echo "   4. Set up Application Load Balancer"
        echo "   5. Configure environment variables"
        echo ""
        echo "📚 AWS ECS Tutorial: https://docs.aws.amazon.com/ecs/"
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🔧 Environment Variables Required:"
echo "  DATABASE_URL (provided by platform)"
echo "  REDIS_URL (provided by platform)"
echo "  ELASTICSEARCH_URL (provided by platform)"
echo "  ADZUNA_APP_ID (your Adzuna app ID)"
echo "  ADZUNA_APP_KEY (your Adzuna app key)"
echo "  RAPIDAPI_KEY (your RapidAPI key)"
echo "  APYHUB_API_KEY (your Apyhub key - optional)"
echo ""
echo "📝 Don't forget to:"
echo "  1. Push your code to GitHub/GitLab"
echo "  2. Add API keys in platform dashboard"
echo "  3. Configure custom domain (optional)"
echo "  4. Set up monitoring and alerts"
echo ""
echo "✨ Good luck with your deployment!"
