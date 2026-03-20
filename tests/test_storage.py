"""
Tests for PostgreSQL, Elasticsearch, and Search Router logic.
"""
import pytest
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.postgres import PostgresStorage
from storage.es_indexer import ElasticsearchIndexer
from storage.search import JobSearchService
from utils.models import ProcessedJob, SalaryInfo

# Pytest fixture for a test DB
@pytest.fixture(scope="module")
def pg_storage():
    test_db = os.getenv("POSTGRES_TEST_URL", "sqlite:///:memory:")
    storage = PostgresStorage(database_url=test_db)
    storage.create_tables()
    return storage

@pytest.fixture
def sample_jobs():
    return [
        ProcessedJob(
            fingerprint="test_fingerprint_123",
            title="Senior Python Developer",
            company="TechCorp",
            location="Remote",
            is_remote=True,
            country="India",
            city="Bangalore",
            source_portal="remotive",
            portal_display_name="Remotive",
            source_url="http://example.com/1",
            apply_url="http://example.com/apply/1",
            job_type="Full-time",
            seniority="Senior",
            domain="Software Development",
            skills=["Python", "Django", "SQL"],
            qualifications=["B.Tech"],
            salary=SalaryInfo(raw="$100k-$150k", min_value=100000, max_value=150000, currency="USD", period="yearly", is_disclosed=True),
            posted_at=datetime.utcnow(),
            scraped_at=datetime.utcnow(),
            processed_at=datetime.utcnow(),
            description_clean="Looking for python developer.",
            description_summary="Python roles.",
            is_fresher_friendly=False,
            requires_experience="5+ years"
        ),
        ProcessedJob(
            fingerprint="test_fingerprint_456",
            title="Junior Frontend Engineer",
            company="WebStartup",
            location="Bangalore",
            is_remote=False,
            country="India",
            city="Bangalore",
            source_portal="remotive",
            portal_display_name="Remotive",
            source_url="http://example.com/2",
            apply_url="http://example.com/apply/2",
            job_type="Full-time",
            seniority="Entry Level",
            domain="Frontend Development",
            skills=["React", "JavaScript", "HTML"],
            qualifications=["BCA"],
            salary=SalaryInfo(raw="₹4-6 LPA", min_value=400000, max_value=600000, currency="INR", period="yearly", is_disclosed=True),
            posted_at=datetime.utcnow(),
            scraped_at=datetime.utcnow(),
            processed_at=datetime.utcnow(),
            description_clean="Looking for frontend fresher.",
            description_summary="React roles.",
            is_fresher_friendly=True,
            requires_experience="0-1 years"
        ),
        ProcessedJob(
            fingerprint="test_fingerprint_789",
            title="Data Scientist (Python/ML)",
            company="AI Labs",
            location="Remote",
            is_remote=True,
            country="USA",
            city="New York",
            source_portal="remoteok",
            portal_display_name="RemoteOK",
            source_url="http://example.com/3",
            apply_url="http://example.com/apply/3",
            job_type="Contract",
            seniority="Mid",
            domain="Data Science & ML",
            skills=["Python", "Machine Learning", "Pandas"],
            qualifications=["M.Tech"],
            salary=SalaryInfo(raw="Not disclosed", min_value=None, max_value=None, currency="", period="", is_disclosed=False),
            posted_at=datetime.utcnow(),
            scraped_at=datetime.utcnow(),
            processed_at=datetime.utcnow(),
            description_clean="Looking for data scientist.",
            description_summary="ML roles.",
            is_fresher_friendly=False,
            requires_experience="2-4 years"
        )
    ]

# --- Tests for PostgresStorage ---

class TestPostgresStorage:
    def test_save_and_retrieve(self, pg_storage, sample_jobs):
        inserted, skipped = pg_storage.save_jobs(sample_jobs)
        assert inserted == 3
        
        jobs = pg_storage.get_jobs(limit=10)
        assert len(jobs) >= 3
        
    def test_upsert_no_duplicate(self, pg_storage, sample_jobs):
        inserted, skipped = pg_storage.save_jobs([sample_jobs[0]])
        # Should skip since it was already inserted
        assert inserted == 0
        assert skipped == 1
        
    def test_filter_by_domain(self, pg_storage):
        jobs = pg_storage.get_jobs(domain="Data Science & ML")
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Data Scientist (Python/ML)"
        
    def test_filter_by_fresher(self, pg_storage):
        jobs = pg_storage.get_jobs(is_fresher=True)
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Junior Frontend Engineer"

    @pytest.mark.skipif(os.getenv("POSTGRES_TEST_URL", "sqlite:///:memory:").startswith("sqlite"), 
                        reason="tsvector is PG-only, skipping fulltext test on SQLite")
    def test_search_fulltext(self, pg_storage):
        results = pg_storage.search("python developer")
        assert len(results) > 0
        assert results[0]["company"] == "TechCorp"
        assert "rank_score" in results[0]

# --- ES Availability Check ---

def check_es_available():
    try:
        es = ElasticsearchIndexer()
        return es.available
    except Exception:
        return False

es_available = check_es_available()

# --- Tests for ElasticsearchIndexer ---

class TestElasticsearchIndexer:
    @pytest.mark.skipif(not es_available, reason="ES not running")
    def test_index_and_search(self, sample_jobs):
        es = ElasticsearchIndexer()
        
        # Test basic indexing
        result = es.index_jobs(sample_jobs[:2])
        assert result["indexed"] == 2
        
        # Force refresh index to make documents searchable immediately
        es.client.indices.refresh(index=es.index_name)
        
        # Test basic search
        res = es.search(query="Python Developer")
        assert res["total"] >= 1
        assert res["hits"][0]["title"] == "Senior Python Developer"

    @pytest.mark.skipif(not es_available, reason="ES not running")
    def test_bulk_index(self, sample_jobs):
        es = ElasticsearchIndexer()
        
        # We simulate bulk by sending multiple copies with different IDs
        import copy
        bulk_jobs = []
        for i in range(50):
            j = copy.deepcopy(sample_jobs[0])
            j.fingerprint = f"bulk_fp_{i}"
            bulk_jobs.append(j)
            
        result = es.index_jobs(bulk_jobs)
        assert result["indexed"] == 50
        
    @pytest.mark.skipif(not es_available, reason="ES not running")
    def test_top_skills_aggregation(self, sample_jobs):
        es = ElasticsearchIndexer()
        es.index_jobs(sample_jobs)
        es.client.indices.refresh(index=es.index_name)
        
        skills = es.get_top_skills()
        assert len(skills) > 0
        
        # Ensure 'Python' mapping is counted
        python_skill = next((s for s in skills if s["skill"] == "Python"), None)
        assert python_skill is not None
        assert python_skill["count"] >= 1
        
    def test_unavailable_graceful(self):
        # Point to an invalid URL so the connection fails
        es = ElasticsearchIndexer(url="http://invalid-es-url.local:9200")
        assert es.available == False
        # Trying a method should raise RuntimeError gracefully
        with pytest.raises(RuntimeError):
            es.get_job_count()


# --- Tests for JobSearchService ---

class TestJobSearchService:
    def test_fallback_to_pg(self):
        svc = JobSearchService()
        # Force ES to be unavailable
        svc._es.available = False
        
        result = svc.search(query="test fallback query")
        assert result["source"] == "pg"
        assert "hits" in result
        
    def test_source_field(self):
        svc = JobSearchService()
        result = svc.search(query="")
        if svc._es.available:
            assert result["source"] == "es"
        else:
            assert result["source"] == "pg"
