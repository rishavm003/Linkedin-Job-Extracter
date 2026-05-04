"""Tests for jobs API endpoints."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient


class TestJobsListEndpoint:
    """Test the /api/jobs endpoint."""
    
    def test_returns_200(self, client: TestClient):
        """GET /api/jobs returns 200."""
        response = client.get("/api/jobs")
        assert response.status_code == 200
    
    def test_response_schema(self, client: TestClient):
        """Response matches JobListResponse shape."""
        response = client.get("/api/jobs?page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert "source" in data
        
        # Check job structure
        if data["jobs"]:
            job = data["jobs"][0]
            required_fields = [
                "id", "title", "company", "location", "is_remote",
                "source_portal", "portal_display_name", "apply_url",
                "job_type", "seniority", "domain", "skills", "salary",
                "scraped_at", "description_summary", "is_fresher_friendly"
            ]
            for field in required_fields:
                assert field in job
    
    def test_pagination(self, client: TestClient):
        """page=2 returns different results than page=1."""
        response1 = client.get("/api/jobs?page=1&page_size=2")
        response2 = client.get("/api/jobs?page=2&page_size=2")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # If there are enough jobs, pages should be different
        if data1["total"] > 2:
            job_ids_1 = [job["id"] for job in data1["jobs"]]
            job_ids_2 = [job["id"] for job in data2["jobs"]]
            # Should not have overlapping job IDs (unless very few jobs)
            assert len(set(job_ids_1) & set(job_ids_2)) == 0
    
    def test_page_size(self, client: TestClient):
        """page_size=5 returns max 5 jobs."""
        response = client.get("/api/jobs?page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["jobs"]) <= 5
        assert data["page_size"] == 5
    
    def test_filter_domain(self, client: TestClient, seeded_db):
        """domain filter returns only that domain."""
        response = client.get("/api/jobs?domain=Software Development")
        assert response.status_code == 200
        
        data = response.json()
        for job in data["jobs"]:
            assert job["domain"] == "Software Development"
    
    def test_filter_is_remote(self, client: TestClient, seeded_db):
        """is_remote=true only returns remote jobs."""
        response = client.get("/api/jobs?is_remote=true")
        assert response.status_code == 200
        
        data = response.json()
        for job in data["jobs"]:
            assert job["is_remote"] is True
    
    def test_filter_is_fresher(self, client: TestClient, seeded_db):
        """is_fresher=true only returns fresher-friendly jobs."""
        response = client.get("/api/jobs?is_fresher=true")
        assert response.status_code == 200
        
        data = response.json()
        for job in data["jobs"]:
            assert job["is_fresher_friendly"] is True
    
    def test_filter_skills(self, client: TestClient, seeded_db):
        """skills filter returns jobs with those skills."""
        response = client.get("/api/jobs?skills=python")
        assert response.status_code == 200
        
        data = response.json()
        for job in data["jobs"]:
            # Check if python is in skills (case-insensitive)
            skills_lower = [s.lower() for s in job["skills"]]
            assert "python" in skills_lower
    
    def test_filter_combined(self, client: TestClient, seeded_db):
        """Multiple filters work together."""
        response = client.get("/api/jobs?is_fresher=true&is_remote=true")
        assert response.status_code == 200
        
        data = response.json()
        for job in data["jobs"]:
            assert job["is_fresher_friendly"] is True
            assert job["is_remote"] is True
    
    def test_invalid_page_size(self, client: TestClient):
        """page_size=500 returns 422."""
        response = client.get("/api/jobs?page_size=500")
        assert response.status_code == 422


class TestJobsSearchEndpoint:
    """Test the /api/jobs/search endpoint."""
    
    def test_search_returns_results(self, client: TestClient, seeded_db):
        """GET /api/jobs/search?q=python returns jobs."""
        response = client.get("/api/jobs/search?q=python")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert "query" in data
        assert "source" in data
        assert data["query"] == "python"
    
    def test_search_echoes_query(self, client: TestClient):
        """Response.query matches the search query."""
        response = client.get("/api/jobs/search?q=developer")
        assert response.status_code == 200
        
        data = response.json()
        assert data["query"] == "developer"
    
    def test_search_too_short(self, client: TestClient):
        """q='a' returns 422 (min length 2)."""
        response = client.get("/api/jobs/search?q=a")
        assert response.status_code == 422
    
    def test_search_no_results(self, client: TestClient):
        """Nonexistent query returns empty list, not 500."""
        response = client.get("/api/jobs/search?q=xyznonexistentrole123")
        assert response.status_code == 200
        
        data = response.json()
        assert data["jobs"] == []
        assert data["total"] == 0


class TestJobDetailEndpoint:
    """Test the /api/jobs/{job_id} endpoint."""
    
    def test_existing_job(self, client: TestClient, seeded_db):
        """GET /api/jobs/{valid_id} returns 200 + JobDetail."""
        # First get a valid job ID
        list_response = client.get("/api/jobs?page_size=1")
        assert list_response.status_code == 200
        
        jobs = list_response.json()["jobs"]
        if jobs:
            job_id = jobs[0]["id"]
            
            detail_response = client.get(f"/api/jobs/{job_id}")
            assert detail_response.status_code == 200
            
            job_detail = detail_response.json()
            # Should have all JobDetail fields
            required_fields = [
                "id", "title", "company", "location", "is_remote",
                "source_portal", "portal_display_name", "apply_url",
                "job_type", "seniority", "domain", "skills", "salary",
                "scraped_at", "description_summary", "is_fresher_friendly",
                "qualifications", "soft_skills", "description_clean",
                "fingerprint"
            ]
            for field in required_fields:
                assert field in job_detail
    
    def test_similar_jobs(self, client: TestClient, seeded_db):
        """Response includes similar_jobs list."""
        # Get a job with domain "Software Development"
        list_response = client.get("/api/jobs?domain=Software Development&page_size=1")
        assert list_response.status_code == 200
        
        jobs = list_response.json()["jobs"]
        if jobs:
            job_id = jobs[0]["id"]
            
            detail_response = client.get(f"/api/jobs/{job_id}")
            assert detail_response.status_code == 200
            
            job_detail = detail_response.json()
            assert "similar_jobs" in job_detail
            assert isinstance(job_detail["similar_jobs"], list)
    
    def test_not_found(self, client: TestClient):
        """GET /api/jobs/nonexistent-id returns 404."""
        response = client.get("/api/jobs/nonexistent-id")
        assert response.status_code == 404
    
    def test_detail_has_description(self, client: TestClient, seeded_db):
        """description_clean field present in detail."""
        # Get a valid job ID
        list_response = client.get("/api/jobs?page_size=1")
        assert list_response.status_code == 200
        
        jobs = list_response.json()["jobs"]
        if jobs:
            job_id = jobs[0]["id"]
            
            detail_response = client.get(f"/api/jobs/{job_id}")
            assert detail_response.status_code == 200
            
            job_detail = detail_response.json()
            assert "description_clean" in job_detail
            assert isinstance(job_detail["description_clean"], str)


class TestMetaEndpoints:
    """Test metadata endpoints."""
    
    def test_portals(self, client: TestClient, seeded_db):
        """GET /api/jobs/portals returns list with portal + count."""
        response = client.get("/api/jobs/portals")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            portal = data[0]
            assert "portal" in portal
            assert "display_name" in portal
            assert "count" in portal
            assert isinstance(portal["count"], int)
    
    def test_domains(self, client: TestClient, seeded_db):
        """GET /api/jobs/domains returns list with domain + count."""
        response = client.get("/api/jobs/domains")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            domain = data[0]
            assert "domain" in domain
            assert "count" in domain
            assert isinstance(domain["count"], int)
    
    def test_skills(self, client: TestClient, seeded_db):
        """GET /api/jobs/skills returns list with skill + count."""
        response = client.get("/api/jobs/skills")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            skill = data[0]
            assert "skill" in skill
            assert "count" in skill
            assert isinstance(skill["count"], int)
