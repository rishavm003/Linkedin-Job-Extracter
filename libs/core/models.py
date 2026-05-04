"""
Pydantic models — the data contracts used across the entire pipeline.
Every scraper outputs a RawJob. The NLP pipeline produces a ProcessedJob.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator
import hashlib
import re


class RawJob(BaseModel):
    """
    Raw output from any scraper — minimal validation, just capture everything.
    """
    source_portal: str                   # e.g. "remotive", "naukri"
    source_url: str                      # the listing URL (apply link)
    title: str
    company: str
    location: Optional[str] = None
    description: str
    salary_raw: Optional[str] = None     # e.g. "₹3–5 LPA", "Not disclosed"
    job_type: Optional[str] = None       # "Full-time", "Internship", etc.
    posted_date_raw: Optional[str] = None
    scraped_at: datetime = None
    raw_tags: list[str] = []

    def __init__(self, **data):
        if data.get("scraped_at") is None:
            data["scraped_at"] = datetime.utcnow()
        super().__init__(**data)

    @property
    def fingerprint(self) -> str:
        """SHA-256 hash used for deduplication."""
        content = f"{self.title.lower().strip()}{self.company.lower().strip()}{self.source_portal}"
        return hashlib.sha256(content.encode()).hexdigest()


class SalaryInfo(BaseModel):
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    currency: Optional[str] = None       # "INR", "USD", etc.
    period: Optional[str] = None         # "yearly", "monthly", "hourly"
    is_disclosed: bool = False
    raw: Optional[str] = None


class ProcessedJob(BaseModel):
    """
    Fully enriched job record after NLP processing.
    This is what gets stored in the database and served by the API.
    """
    # Identity
    id: Optional[str] = None            # UUID assigned at storage time
    fingerprint: str                    # from RawJob

    # Core fields (cleaned)
    title: str
    company: str
    location: str = "Remote / Not specified"
    is_remote: bool = False
    country: Optional[str] = None
    city: Optional[str] = None

    # URLs
    source_portal: str
    apply_url: str                       # direct apply link
    portal_display_name: str             # "LinkedIn", "Naukri", etc.

    # Job metadata
    job_type: str = "Full-time"          # "Internship", "Contract", etc.
    seniority: str = "Entry Level"       # "Fresher", "Junior", "Mid", "Senior"
    domain: str = "Other"               # from JOB_DOMAINS

    # Extracted by NLP
    skills: list[str] = []              # normalised skill names
    qualifications: list[str] = []
    soft_skills: list[str] = []
    salary: SalaryInfo = SalaryInfo()

    # Dates
    posted_at: Optional[datetime] = None
    scraped_at: datetime = None
    processed_at: datetime = None

    # Raw description kept for search indexing
    description_clean: str = ""         # stripped HTML / noise
    description_summary: str = ""       # first 300 chars

    # Freshers-relevant flags
    is_fresher_friendly: bool = False
    requires_experience: Optional[str] = None   # "0-1 years", "1-2 years"

    def __init__(self, **data):
        now = datetime.utcnow()
        if data.get("scraped_at") is None:
            data["scraped_at"] = now
        if data.get("processed_at") is None:
            data["processed_at"] = now
        super().__init__(**data)

    @field_validator("title", "company", mode="before")
    @classmethod
    def clean_text(cls, v: str) -> str:
        if v:
            v = re.sub(r"\s+", " ", v).strip()
        return v or ""

    @property
    def skills_display(self) -> str:
        return ", ".join(self.skills[:8])

    def to_es_doc(self) -> dict:
        """Serialize for Elasticsearch indexing."""
        return {
            **self.model_dump(),
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
