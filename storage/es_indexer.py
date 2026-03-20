"""
Elasticsearch indexing and search functionality.
"""
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError
from config.settings import ELASTICSEARCH_URL, ELASTICSEARCH_INDEX
from utils.models import ProcessedJob
from utils.logger import logger

class ElasticsearchIndexer:
    """
    Handles indexing ProcessedJobs into Elasticsearch and querying the index.
    """

    def __init__(self, url: str = ELASTICSEARCH_URL, index_name: str = ELASTICSEARCH_INDEX):
        self.url = url
        self.index_name = index_name
        self.available = False
        
        try:
            self.client = Elasticsearch(
                self.url,
                request_timeout=10,
                max_retries=3,
                retry_on_timeout=True
            )
            # Check availability 
            if self.client.ping():
                self.available = True
                self._create_index_if_not_exists()
                logger.info(f"[Storage] Elasticsearch connected at {self.url}")
            else:
                logger.warning(f"[Storage] Elasticsearchping failed at {self.url}. Operating without ES.")
        except ConnectionError as e:
            logger.warning(f"[Storage] Elasticsearch connection failed: {e}. Operating without ES.")
        except Exception as e:
            logger.warning(f"[Storage] Unexpected error connecting to ES: {e}. Operating without ES.")

    def _check_available(self):
        """Checker wrapper for methods that require ES"""
        if not self.available:
            raise RuntimeError("Elasticsearch not available")

    def _create_index_if_not_exists(self):
        """Define mapping and create index if not existing."""
        if not self.client.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "fingerprint": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "english",
                            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
                        },
                        "company": {
                            "type": "text",
                            "analyzer": "english",
                            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
                        },
                        "location": {"type": "keyword"},
                        "is_remote": {"type": "boolean"},
                        "source_portal": {"type": "keyword"},
                        "portal_display_name": {"type": "keyword"},
                        "apply_url": {"type": "keyword", "index": False},
                        "job_type": {"type": "keyword"},
                        "seniority": {"type": "keyword"},
                        "domain": {"type": "keyword"},
                        "skills": {"type": "keyword"},
                        "qualifications": {"type": "keyword"},
                        "salary_min": {"type": "float"},
                        "salary_max": {"type": "float"},
                        "salary_currency": {"type": "keyword"},
                        "salary_disclosed": {"type": "boolean"},
                        "posted_at": {"type": "date"},
                        "scraped_at": {"type": "date"},
                        "description_clean": {
                            "type": "text",
                            "analyzer": "english"
                        },
                        "description_summary": {
                            "type": "text",
                            "analyzer": "english"
                        },
                        "is_fresher_friendly": {"type": "boolean"},
                        "requires_experience": {"type": "keyword"}
                    }
                }
            }
            self.client.indices.create(index=self.index_name, body=mapping)
            logger.info(f"[Storage] Created ES index: {self.index_name}")

    def index_jobs(self, jobs: list[ProcessedJob]) -> dict:
        """
        Bulk index jobs into Elasticsearch.
        Uses fingerprint as the document ID for upserting.
        """
        self._check_available()
        
        if not jobs:
            return {"indexed": 0, "failed": 0}

        actions = []
        for job in jobs:
            doc = job.to_es_doc()
            actions.append({
                "_op_type": "index",
                "_index": self.index_name,
                "_id": job.fingerprint,
                "_source": doc
            })

        indexed = 0
        failed = 0
        
        try:
            success, errors = helpers.bulk(
                self.client,
                actions,
                stats_only=False,
                raise_on_error=False,
                raise_on_exception=False
            )
            indexed = success
            if errors:
                failed = len(errors)
                for err in errors:
                    logger.warning(f"[Storage] ES Index Error: {err}")
        except Exception as e:
            logger.warning(f"[Storage] Bulk indexing encountered an error: {e}")
            
        logger.info(f"[Storage] ES Bulk index: {indexed} indexed, {failed} failed")
        return {"indexed": indexed, "failed": failed}

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
        Execute full-text search with filters on ES.
        """
        self._check_available()

        es_query = {"bool": {"must": [], "filter": []}}

        if query and query.strip():
            es_query["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "company^2", "description_clean", "skills^2"]
                }
            })
        else:
            es_query["bool"]["must"].append({"match_all": {}})

        if domain:
            es_query["bool"]["filter"].append({"term": {"domain": domain}})
        if seniority:
            es_query["bool"]["filter"].append({"term": {"seniority": seniority}})
        if is_remote is not None:
            es_query["bool"]["filter"].append({"term": {"is_remote": is_remote}})
        if is_fresher is not None:
            es_query["bool"]["filter"].append({"term": {"is_fresher_friendly": is_fresher}})
        if portal:
            es_query["bool"]["filter"].append({"term": {"source_portal": portal}})
            
        if skills:
            es_query["bool"]["filter"].append({"terms": {"skills": skills}})

        if salary_min is not None or salary_max is not None:
            range_filter = {}
            if salary_min is not None:
                range_filter["gte"] = salary_min
            if salary_max is not None:
                range_filter["lte"] = salary_max
                
            es_query["bool"]["filter"].append({
                "range": {
                    "salary_min": range_filter
                }
            })

        body = {
            "query": es_query,
            "size": limit,
            "from": offset,
            "sort": ["_score", {"scraped_at": "desc"}]
        }

        response = self.client.search(index=self.index_name, body=body)
        
        hits = []
        for hit in response["hits"]["hits"]:
            doc = hit["_source"]
            doc["_score"] = hit["_score"]
            hits.append(doc)
            
        return {
            "hits": hits,
            "total": response["hits"]["total"]["value"]
        }

    def delete_old_jobs(self, older_than_days: int = 30) -> int:
        """Delete jobs where scraped_at < (now - older_than_days)."""
        self._check_available()
        
        target_date = datetime.utcnow() - timedelta(days=older_than_days)
        body = {
            "query": {
                "range": {
                    "scraped_at": {
                        "lt": target_date.isoformat()
                    }
                }
            }
        }
        
        response = self.client.delete_by_query(index=self.index_name, body=body)
        return response.get("deleted", 0)

    def get_top_skills(self, size: int = 20) -> list[dict]:
        """Aggregate top skills using ES terms aggregation."""
        self._check_available()
        
        body = {
            "size": 0,
            "aggs": {
                "top_skills": {
                    "terms": {
                        "field": "skills",
                        "size": size
                    }
                }
            }
        }
        
        response = self.client.search(index=self.index_name, body=body)
        buckets = response["aggregations"]["top_skills"]["buckets"]
        
        return [{"skill": b["key"], "count": b["doc_count"]} for b in buckets]

    def get_domain_distribution(self) -> list[dict]:
        """Aggregate domain distribution using ES terms aggregation."""
        self._check_available()
        
        body = {
            "size": 0,
            "aggs": {
                "domains": {
                    "terms": {
                        "field": "domain",
                        "size": 50
                    }
                }
            }
        }
        
        response = self.client.search(index=self.index_name, body=body)
        buckets = response["aggregations"]["domains"]["buckets"]
        
        return [{"domain": b["key"], "count": b["doc_count"]} for b in buckets]

    def get_job_count(self) -> int:
        """Total number of documents in the index."""
        self._check_available()
        
        response = self.client.count(index=self.index_name)
        return response["count"]
