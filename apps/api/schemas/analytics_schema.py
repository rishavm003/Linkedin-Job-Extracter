"""Pydantic schemas for analytics API responses."""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_jobs: int
    fresher_friendly: int
    remote_jobs: int
    portals_tracked: int
    domains_covered: int
    last_scraped_at: Optional[datetime] = None


class DomainDistribution(BaseModel):
    domain: str
    count: int
    percentage: float


class SeniorityBreakdown(BaseModel):
    seniority: str
    count: int
    percentage: float


class PortalDistribution(BaseModel):
    portal: str
    display_name: str
    count: int
    percentage: float


class SalaryRange(BaseModel):
    domain: str
    avg_min: Optional[float] = None
    avg_max: Optional[float] = None
    currency: str


class TrendingSkill(BaseModel):
    skill: str
    count_this_week: int
    count_last_week: int
    change_pct: float  # positive = growing, negative = declining


class RemoteVsOnsite(BaseModel):
    remote: int
    onsite: int
    remote_percentage: float


class AnalyticsDashboard(BaseModel):
    """Single endpoint that returns everything the dashboard needs."""
    summary: SummaryResponse
    domain_distribution: List[DomainDistribution]
    top_skills: List[dict]  # Using dict to match SkillInfo shape
    seniority_breakdown: List[SeniorityBreakdown]
    portal_distribution: List[PortalDistribution]
    remote_vs_onsite: RemoteVsOnsite
    source: str
