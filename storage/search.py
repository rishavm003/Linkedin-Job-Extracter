"""
Unified search interface routing queries to Elasticsearch if available,
with graceful fallback to PostgreSQL.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.postgres import PostgresStorage
from storage.es_indexer import ElasticsearchIndexer
from utils.logger import logger

class JobSearchService:
    """
    Search service for job listings and analytics.
    Attempts Elasticsearch first, falls back to PostgreSQL automatically.
    """

    def __init__(self):
        self._es = ElasticsearchIndexer()
        self._pg = PostgresStorage()

    def search(
        self,
        query: str = None,
        domain: str = None,
        seniority: str = None,
        is_remote: bool = None,
        is_fresher: bool = None,
        portal: str = None,
        skills: list[str] = None,
        salary_min: float = None,
        salary_max: float = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        Unified search endpoint.
        Returns:
            {"hits": [list of job dicts], "total": int, "source": "es"|"pg"}
        """
        if self._es.available:
            try:
                res = self._es.search(
                    query=query,
                    domain=domain,
                    seniority=seniority,
                    is_remote=is_remote,
                    is_fresher=is_fresher,
                    portal=portal,
                    skills=skills,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    limit=limit,
                    offset=offset
                )
                res["source"] = "es"
                return res
            except Exception as e:
                logger.warning(f"[SearchRouter] ES search failed: {e}. Falling back to PostgreSQL.")
        
        # Fallback to PostgreSQL
        hits = self._pg.search(
            query=query or "",
            domain=domain,
            seniority=seniority,
            is_remote=is_remote,
            is_fresher=is_fresher,
            portal=portal,
            limit=limit,
            offset=offset
        )
        total = self._pg.count_search(
            query=query or "",
            domain=domain,
            seniority=seniority,
            is_remote=is_remote,
            is_fresher=is_fresher,
            portal=portal
        )
        
        return {
            "hits": hits,
            "total": total,
            "source": "pg"
        }

    def get_analytics(self) -> dict:
        """
        Unified analytics endpoint. 
        Tries ES aggregations first, falls back to PostgreSQL stats.
        """
        if self._es.available:
            try:
                total_jobs = self._es.get_job_count()
                
                # We can perform a couple of exact counts if needed, 
                # but to mimic PG stats, we query 0-limit counts
                fresher_res = self._es.search(is_fresher=True, limit=0)
                remote_res = self._es.search(is_remote=True, limit=0)
                
                top_skills = self._es.get_top_skills(size=20)
                domain_dist = self._es.get_domain_distribution()
                
                return {
                    "total_jobs": total_jobs,
                    "fresher_friendly": fresher_res["total"],
                    "remote_jobs": remote_res["total"],
                    "domain_distribution": domain_dist,
                    "top_skills": top_skills,
                    "source": "es"
                }
            except Exception as e:
                logger.warning(f"[SearchRouter] ES analytics failed: {e}. Falling back to PostgreSQL.")
        
        # Fallback to PostgreSQL
        stats = self._pg.get_stats()
        stats["source"] = "pg"
        return stats
