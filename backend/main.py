"""FastAPI application factory for JobExtractor backend."""
from __future__ import annotations
import sys
import os
from contextlib import asynccontextmanager

# Add parent directory to path to import jobextractor modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import logger from jobextractor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'jobextractor'))
from utils.logger import logger

# Import routers
from routers import jobs, analytics, health, ai_query


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("JobExtractor API starting up...")
    
    # Verify PostgreSQL connection
    try:
        from dependencies import get_postgres
        pg = get_postgres()
        job_count = pg.get_job_count()
        logger.info(f"PostgreSQL connected. Jobs in DB: {job_count}")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed: {e}")
    
    # Verify ES connection
    try:
        from dependencies import get_es
        es = get_es()
        if es.available:
            es_count = es.get_job_count()
            logger.info(f"Elasticsearch connected. Jobs in index: {es_count}")
        else:
            logger.info("Elasticsearch unavailable - will use PostgreSQL fallback")
    except Exception as e:
        logger.warning(f"Elasticsearch check failed: {e}")
    
    logger.info("JobExtractor API started. Docs at /docs")
    
    yield
    
    # Shutdown
    logger.info("JobExtractor API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="JobExtractor API",
    description="Multi-portal job extraction and analytics API for Indian freshers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://*.vercel.app",
]

# Add frontend URL from env if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: Rate limiting disabled for testing

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Include routers
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(analytics.router)
app.include_router(ai_query.router)

# Root redirect to docs
@app.get("/")
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")


# Health check endpoint (direct access without rate limiting)
@app.get("/health")
async def health_no_rate_limit():
    """Health check without rate limiting for monitoring systems."""
    return await health.health_check()
