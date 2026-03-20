"""Health check router."""
from __future__ import annotations
from typing import Dict, Any
import sys
import os

# Add parent directory to path to import jobextractor modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import get_postgres, get_es

router = APIRouter(prefix="/api", tags=["health"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/health", summary="Health check endpoint")
async def health_check():
    """Returns health status of all services. Always returns 200."""
    health: Dict[str, Any] = {
        "status": "ok",
        "postgres": "connected",
        "elasticsearch": "connected",
        "redis": "connected",
        "jobs_in_db": 0,
        "version": "1.0.0"
    }
    
    # Check PostgreSQL
    try:
        pg = get_postgres()
        health["jobs_in_db"] = pg.get_job_count()
    except Exception as e:
        health["postgres"] = f"error: {str(e)[:100]}"
    
    # Check Elasticsearch
    try:
        es = get_es()
        if es.available:
            health["elasticsearch"] = "connected"
        else:
            health["elasticsearch"] = "unavailable"
    except Exception as e:
        health["elasticsearch"] = f"error: {str(e)[:100]}"
    
    # Check Redis
    try:
        redis_client = _get_redis()
        if redis_client:
            redis_client.ping()
            health["redis"] = "connected"
        else:
            health["redis"] = "unavailable"
    except Exception as e:
        health["redis"] = "unavailable"
    
    return health


@router.get("/health/ready", summary="Readiness check for load balancer")
async def readiness_check():
    """Returns 200 if PostgreSQL is reachable, 503 otherwise."""
    try:
        pg = get_postgres()
        pg.get_job_count()  # Simple query to test connection
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"PostgreSQL unavailable: {str(e)[:100]}"
        )


def _get_redis():
    """Get Redis client if available."""
    try:
        import redis
        from config.settings import REDIS_URL
        return redis.from_url(REDIS_URL, decode_responses=True)
    except:
        return None
