#!/bin/bash
echo "Stopping all JobExtractor services..."
docker compose -f docker-compose.full.yml down
echo "All services stopped."
echo ""
echo "To also remove all data volumes (CAREFUL — deletes all job data):"
echo "  docker compose -f docker-compose.full.yml down -v"
