"""Pydantic schemas for job-related API responses."""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SalarySchema(BaseModel):
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    currency: Optional[str] = None
    period: Optional[str] = None
    is_disclosed: bool
    raw: Optional[str] = None


class JobSummary(BaseModel):
    """Used in list views — no full description."""
    id: str
    title: str
    company: str
    location: str
    is_remote: bool
    source_portal: str
    portal_display_name: str
    apply_url: str
    job_type: str
    seniority: str
    domain: str
    skills: List[str]
    salary: SalarySchema
    posted_at: Optional[datetime] = None
    scraped_at: datetime
    description_summary: str
    is_fresher_friendly: bool
    requires_experience: Optional[str] = None


class JobDetail(JobSummary):
    """Used in detail view — includes full description."""
    qualifications: List[str]
    soft_skills: List[str]
    description_clean: str
    country: Optional[str] = None
    city: Optional[str] = None
    fingerprint: str


class JobListResponse(BaseModel):
    jobs: List[JobSummary]
    total: int
    page: int
    page_size: int
    total_pages: int
    source: str  # "es" or "pg" — which backend served this


class JobSearchResponse(BaseModel):
    jobs: List[JobSummary]
    total: int
    query: str
    source: str


class PortalInfo(BaseModel):
    portal: str
    display_name: str
    count: int


class DomainInfo(BaseModel):
    domain: str
    count: int


class SkillInfo(BaseModel):
    skill: str
    count: int
