"""Pytest configuration and fixtures for backend tests."""
from __future__ import annotations
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'jobextractor'))

from main import app
from utils.models import ProcessedJob, SalaryInfo


@pytest.fixture
def client():
    """Create FastAPI test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_jobs() -> List[Dict[str, Any]]:
    """Return 5 hardcoded job dicts covering different scenarios."""
    now = datetime.utcnow()
    return [
        {
            "id": "job-1",
            "fingerprint": "fp-1",
            "title": "Python Developer (Fresher)",
            "company": "TechCorp India",
            "location": "Bangalore, Karnataka",
            "is_remote": False,
            "country": "India",
            "city": "Bangalore",
            "source_portal": "naukri",
            "portal_display_name": "Naukri",
            "apply_url": "https://naukri.com/job/1",
            "job_type": "Full-time",
            "seniority": "Entry Level",
            "domain": "Software Development",
            "skills": ["python", "django", "sql", "api"],
            "qualifications": ["B.Tech", "B.Sc"],
            "soft_skills": ["communication", "teamwork"],
            "salary_min": 300000.0,
            "salary_max": 600000.0,
            "salary_currency": "INR",
            "salary_period": "yearly",
            "salary_disclosed": True,
            "salary_raw": "3-6 LPA",
            "posted_at": now,
            "scraped_at": now,
            "processed_at": now,
            "description_clean": "We are looking for a Python developer fresher...",
            "description_summary": "Python developer position for freshers in Bangalore.",
            "is_fresher_friendly": True,
            "requires_experience": "0-1 years"
        },
        {
            "id": "job-2",
            "fingerprint": "fp-2",
            "title": "Remote Data Scientist",
            "company": "DataAnalytics Inc",
            "location": "Remote",
            "is_remote": True,
            "country": None,
            "city": None,
            "source_portal": "remoteok",
            "portal_display_name": "RemoteOK",
            "apply_url": "https://remoteok.io/job/2",
            "job_type": "Full-time",
            "seniority": "Mid Level",
            "domain": "Data Science & ML",
            "skills": ["python", "pandas", "machine learning", "statistics"],
            "qualifications": ["M.Sc", "PhD"],
            "soft_skills": ["analytical", "problem solving"],
            "salary_min": 1500000.0,
            "salary_max": 2500000.0,
            "salary_currency": "INR",
            "salary_period": "yearly",
            "salary_disclosed": True,
            "salary_raw": "15-25 LPA",
            "posted_at": now,
            "scraped_at": now,
            "processed_at": now,
            "description_clean": "Remote data scientist position with ML focus...",
            "description_summary": "Remote data scientist role with competitive salary.",
            "is_fresher_friendly": False,
            "requires_experience": "2-4 years"
        },
        {
            "id": "job-3",
            "fingerprint": "fp-3",
            "title": "Frontend Developer Intern",
            "company": "WebStart",
            "location": "Mumbai, Maharashtra",
            "is_remote": False,
            "country": "India",
            "city": "Mumbai",
            "source_portal": "naukri",
            "portal_display_name": "Naukri",
            "apply_url": "https://naukri.com/job/3",
            "job_type": "Internship",
            "seniority": "Intern",
            "domain": "Frontend Development",
            "skills": ["react", "javascript", "css", "html"],
            "qualifications": ["B.Tech", "BCA"],
            "soft_skills": ["learning", "creativity"],
            "salary_min": 10000.0,
            "salary_max": 20000.0,
            "salary_currency": "INR",
            "salary_period": "monthly",
            "salary_disclosed": True,
            "salary_raw": "10-20k per month",
            "posted_at": now,
            "scraped_at": now,
            "processed_at": now,
            "description_clean": "Frontend development internship opportunity...",
            "description_summary": "Frontend intern position in Mumbai with stipend.",
            "is_fresher_friendly": True,
            "requires_experience": "0-6 months"
        },
        {
            "id": "job-4",
            "fingerprint": "fp-4",
            "title": "Senior DevOps Engineer",
            "company": "CloudTech Solutions",
            "location": "Pune, Maharashtra",
            "is_remote": False,
            "country": "India",
            "city": "Pune",
            "source_portal": "linkedin",
            "portal_display_name": "LinkedIn",
            "apply_url": "https://linkedin.com/job/4",
            "job_type": "Full-time",
            "seniority": "Senior",
            "domain": "DevOps",
            "skills": ["docker", "kubernetes", "aws", "jenkins"],
            "qualifications": ["B.Tech", "M.Tech"],
            "soft_skills": ["leadership", "mentoring"],
            "salary_min": 2000000.0,
            "salary_max": 3500000.0,
            "salary_currency": "INR",
            "salary_period": "yearly",
            "salary_disclosed": True,
            "salary_raw": "20-35 LPA",
            "posted_at": now,
            "scraped_at": now,
            "processed_at": now,
            "description_clean": "Senior DevOps engineer with cloud expertise...",
            "description_summary": "Senior DevOps role requiring 5+ years experience.",
            "is_fresher_friendly": False,
            "requires_experience": "5+ years"
        },
        {
            "id": "job-5",
            "fingerprint": "fp-5",
            "title": "Full Stack Developer (Remote)",
            "company": "StartupHub",
            "location": "Remote",
            "is_remote": True,
            "country": None,
            "city": None,
            "source_portal": "remotive",
            "portal_display_name": "Remotive",
            "apply_url": "https://remotive.io/job/5",
            "job_type": "Full-time",
            "seniority": "Entry Level",
            "domain": "Full Stack Development",
            "skills": ["javascript", "nodejs", "react", "mongodb"],
            "qualifications": ["B.Tech", "B.Sc"],
            "soft_skills": ["self-starter", "adaptability"],
            "salary_min": 800000.0,
            "salary_max": 1200000.0,
            "salary_currency": "INR",
            "salary_period": "yearly",
            "salary_disclosed": True,
            "salary_raw": "8-12 LPA",
            "posted_at": now,
            "scraped_at": now,
            "processed_at": now,
            "description_clean": "Remote full stack developer for growing startup...",
            "description_summary": "Remote full stack role, fresher-friendly with good salary.",
            "is_fresher_friendly": True,
            "requires_experience": "0-2 years"
        }
    ]


@pytest.fixture
def seeded_db(sample_jobs):
    """Insert sample jobs into PostgreSQL for testing."""
    # Skip if test database not configured
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        pytest.skip("TEST_DATABASE_URL not set")
    
    from storage.postgres import PostgresStorage
    
    # Use test database
    pg = PostgresStorage(database_url=test_db_url)
    pg.create_tables()
    
    # Convert to ProcessedJob objects
    processed_jobs = []
    for job_dict in sample_jobs:
        # Create SalaryInfo
        salary = SalaryInfo(
            min_value=job_dict["salary_min"],
            max_value=job_dict["salary_max"],
            currency=job_dict["salary_currency"],
            period=job_dict["salary_period"],
            is_disclosed=job_dict["salary_disclosed"],
            raw=job_dict["salary_raw"]
        )
        
        # Create ProcessedJob
        job = ProcessedJob(
            fingerprint=job_dict["fingerprint"],
            title=job_dict["title"],
            company=job_dict["company"],
            location=job_dict["location"],
            is_remote=job_dict["is_remote"],
            country=job_dict["country"],
            city=job_dict["city"],
            source_portal=job_dict["source_portal"],
            portal_display_name=job_dict["portal_display_name"],
            apply_url=job_dict["apply_url"],
            job_type=job_dict["job_type"],
            seniority=job_dict["seniority"],
            domain=job_dict["domain"],
            skills=job_dict["skills"],
            qualifications=job_dict["qualifications"],
            soft_skills=job_dict["soft_skills"],
            salary=salary,
            posted_at=job_dict["posted_at"],
            scraped_at=job_dict["scraped_at"],
            processed_at=job_dict["processed_at"],
            description_clean=job_dict["description_clean"],
            description_summary=job_dict["description_summary"],
            is_fresher_friendly=job_dict["is_fresher_friendly"],
            requires_experience=job_dict["requires_experience"]
        )
        processed_jobs.append(job)
    
    # Save to database
    inserted, skipped = pg.save_jobs(processed_jobs)
    
    yield pg
    
    # Cleanup: delete inserted jobs
    fingerprints = [job["fingerprint"] for job in sample_jobs]
    try:
        with pg.get_session() as session:
            from storage.postgres import JobRecord
            from sqlalchemy import text
            session.execute(text("DELETE FROM jobs WHERE fingerprint = ANY(:fps)"), {"fps": fingerprints})
            session.commit()
    except:
        pass  # Best effort cleanup
