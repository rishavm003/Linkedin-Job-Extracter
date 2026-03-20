"""Dependency injection for FastAPI backend."""
from __future__ import annotations
from functools import lru_cache
from typing import Annotated
import sys
import os

# Add parent directory to path to import jobextractor modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import Depends

from storage.postgres import PostgresStorage
from storage.es_indexer import ElasticsearchIndexer
from storage.search import JobSearchService


@lru_cache(maxsize=1)
def get_postgres() -> PostgresStorage:
    """Singleton PostgresStorage — reused across requests."""
    return PostgresStorage()


@lru_cache(maxsize=1)
def get_es() -> ElasticsearchIndexer:
    """Singleton ES indexer — available=False if ES is down."""
    return ElasticsearchIndexer()


@lru_cache(maxsize=1)
def get_search_service() -> JobSearchService:
    """Singleton search service — handles ES→PG fallback."""
    return JobSearchService()


def pg_dep() -> Annotated[PostgresStorage, Depends]:
    """FastAPI dependency for PostgresStorage."""
    return get_postgres()


def search_dep() -> Annotated[JobSearchService, Depends]:
    """FastAPI dependency for JobSearchService."""
    return get_search_service()


def es_dep() -> Annotated[ElasticsearchIndexer, Depends]:
    """FastAPI dependency for ElasticsearchIndexer."""
    return get_es()
