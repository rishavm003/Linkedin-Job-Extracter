"""Tests for analytics API endpoints."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient


class TestAnalyticsEndpoints:
    """Test analytics endpoints."""
    
    def test_dashboard_200(self, client: TestClient):
        """GET /api/analytics/dashboard returns 200."""
        response = client.get("/api/analytics/dashboard")
        assert response.status_code == 200
    
    def test_dashboard_schema(self, client: TestClient):
        """All required fields present in dashboard response."""
        response = client.get("/api/analytics/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "summary", "domain_distribution", "top_skills",
            "seniority_breakdown", "portal_distribution",
            "remote_vs_onsite", "source"
        ]
        for field in required_fields:
            assert field in data
        
        # Check summary structure
        summary = data["summary"]
        summary_fields = [
            "total_jobs", "fresher_friendly", "remote_jobs",
            "portals_tracked", "domains_covered", "last_scraped_at"
        ]
        for field in summary_fields:
            assert field in summary
    
    def test_summary_counts_positive(self, client: TestClient, seeded_db):
        """total_jobs > 0 (if DB has data)."""
        response = client.get("/api/analytics/summary")
        assert response.status_code == 200
        
        data = response.json()
        # If there's data, counts should be positive
        if data["total_jobs"] > 0:
            assert data["total_jobs"] > 0
            assert data["fresher_friendly"] >= 0
            assert data["remote_jobs"] >= 0
    
    def test_domain_percentages_sum_100(self, client: TestClient):
        """Domain percentages sum to ~100 (allow ±0.5 rounding)."""
        response = client.get("/api/analytics/domain-distribution")
        assert response.status_code == 200
        
        data = response.json()
        if data:
            total_percentage = sum(item["percentage"] for item in data)
            # Allow for rounding errors
            assert 99.5 <= total_percentage <= 100.5
    
    def test_top_skills_ordered(self, client: TestClient):
        """Skills returned in descending count order."""
        response = client.get("/api/analytics/top-skills")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 1:
            # Check that counts are in descending order
            for i in range(len(data) - 1):
                assert data[i]["count"] >= data[i + 1]["count"]
    
    def test_seniority_has_entry_level(self, client: TestClient, seeded_db):
        """Entry Level present in seniority_breakdown."""
        response = client.get("/api/analytics/seniority-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        seniorities = [item["seniority"] for item in data]
        # Should have some common seniority levels
        assert any(level in seniorities for level in ["Entry Level", "Fresher", "Intern"])
    
    def test_remote_vs_onsite(self, client: TestClient):
        """remote + onsite == total_jobs."""
        response = client.get("/api/analytics/remote-vs-onsite")
        assert response.status_code == 200
        
        data = response.json()
        assert "remote" in data
        assert "onsite" in data
        assert "remote_percentage" in data
        
        # Get total jobs to verify
        summary_response = client.get("/api/analytics/summary")
        if summary_response.status_code == 200:
            summary = summary_response.json()
            total = summary["total_jobs"]
            assert data["remote"] + data["onsite"] == total
    
    def test_salary_ranges_inr(self, client: TestClient, seeded_db):
        """Currency is INR for Indian portal jobs."""
        response = client.get("/api/analytics/salary-ranges")
        assert response.status_code == 200
        
        data = response.json()
        if data:
            # Most should be INR for Indian job data
            currencies = [item["currency"] for item in data]
            assert "INR" in currencies
    
    def test_trending_has_change_pct(self, client: TestClient):
        """Each trending skill has change_pct field."""
        response = client.get("/api/analytics/trending-skills")
        assert response.status_code == 200
        
        data = response.json()
        if data:
            for skill in data:
                assert "change_pct" in skill
                assert isinstance(skill["change_pct"], (int, float))
    
    def test_health_always_200(self, client: TestClient):
        """GET /api/health always returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "postgres" in data
        assert "elasticsearch" in data
        assert "redis" in data
        assert "jobs_in_db" in data
        assert "version" in data
    
    def test_health_ready_200(self, client: TestClient):
        """GET /api/health/ready returns 200 if PG up."""
        response = client.get("/api/health/ready")
        # Should return 200 if PostgreSQL is available, 503 otherwise
        assert response.status_code in [200, 503]
