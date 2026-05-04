.PHONY: setup run-worker run-api dev-web migrate-db help

# Default target
help:
	@echo "JobExtractor Platform - Production Management"
	@echo ""
	@echo "Commands:"
	@echo "  make setup        - Install dependencies and setup environment"
	@echo "  make run-worker   - Run the job ingestion pipeline once"
	@echo "  make schedule     - Start the background scheduler"
	@echo "  make run-api      - Start the FastAPI backend"
	@echo "  make dev-web      - Start Next.js frontend in development"
	@echo "  make migrate-db   - Run database migrations (Alembic)"
	@echo "  make docker-up    - Start everything using Docker"
	@echo "  make docker-down  - Stop all Docker services"

setup:
	pip install -r apps/worker/requirements.txt
	pip install -r apps/api/requirements.txt
	cd apps/web && npm install

run-worker:
	python main.py run --db

schedule:
	python main.py schedule --db

run-api:
	cd apps/api && uvicorn main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

migrate-db:
	python main.py db migrate

docker-up:
	docker compose up -d

docker-down:
	docker compose down
