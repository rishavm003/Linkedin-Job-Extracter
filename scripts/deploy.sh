#!/bin/bash
set -e

echo "══════════════════════════════════"
echo "  JobExtractor — Full Stack Deploy"
echo "══════════════════════════════════"

# Check .env exists
if [ ! -f .env ]; then
  echo "ERROR: .env file not found"
  echo "Copy .env.example to .env and fill in your keys"
  exit 1
fi

# Check Docker is running
if ! command -v docker &> /dev/null; then
  echo "ERROR: Docker is not running"
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  echo "ERROR: Docker Compose is not running"
  exit 1
fi

echo ""
echo "Step 1 — Building all Docker images..."
docker compose -f docker-compose.full.yml build --no-cache

echo ""
echo "Step 2 — Starting infrastructure (postgres, redis, es)..."
docker compose -f docker-compose.full.yml up -d postgres redis elasticsearch
echo "Waiting 30 seconds for services to be healthy..."
sleep 30

echo ""
echo "Step 3 — Running database migrations..."
docker compose -f docker-compose.full.yml run --rm backend sh -c \
  "cd /app/backend && python -m alembic upgrade head"

echo ""
echo "Step 4 — Seeding initial job data..."
docker compose -f docker-compose.full.yml run --rm pipeline sh -c \
  "cd /app/jobextractor && python main.py run \
   --portals remotive remoteok arbeitnow \
   --max 100 --db"

echo ""
echo "Step 5 — Starting all services..."
docker compose -f docker-compose.full.yml up -d

echo ""
echo "Step 6 — Waiting for health checks..."
sleep 20

echo ""
echo "Step 7 — Verifying deployment..."
curl -sf http://localhost:8000/api/health && \
  echo "Backend: OK" || echo "Backend: FAILED"
curl -sf http://localhost:3000 && \
  echo "Frontend: OK" || echo "Frontend: FAILED"
curl -sf http://localhost/nginx-health && \
  echo "Nginx: OK" || echo "Nginx: FAILED"

echo ""
echo "════════════════════════════════════"
echo "  Deployment complete!"
echo ""
echo "📊 Service URLs:"
echo "  Frontend:      http://localhost:3000"
echo "  Backend API:   http://localhost:8000"
echo "  API Docs:      http://localhost:8000/docs"
echo "  PostgreSQL:    localhost:5432"
echo "  Redis:         localhost:6379"
echo "  Elasticsearch: localhost:9200"
echo "  Ollama AI:     http://localhost:11434"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs:     docker compose -f docker-compose.full.yml logs -f [service]"
echo "  Stop all:      docker compose -f docker-compose.full.yml down"
echo "  Restart:       docker compose -f docker-compose.full.yml restart [service]"
echo "  Scale backend: docker compose -f docker-compose.full.yml up -d --scale backend=2"
echo ""
echo "📈 Monitoring:"
echo "  Run pipeline:  docker compose -f docker-compose.full.yml exec pipeline python main.py run"
echo "  Check stats:   docker compose -f docker-compose.full.yml exec pipeline python main.py stats"
echo ""
echo "✨ Happy job hunting!"
