"""Analytics router - aggregation and chart data endpoints."""
from __future__ import annotations
from typing import Optional, List, Annotated
import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import jobextractor modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, Query, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from sqlalchemy import text
from storage.search import JobSearchService
from storage.postgres import PostgresStorage
from dependencies import search_dep, pg_dep
from schemas.analytics_schema import (
    AnalyticsDashboard, SummaryResponse, DomainDistribution,
    SeniorityBreakdown, PortalDistribution, SalaryRange,
    TrendingSkill, RemoteVsOnsite
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
limiter = Limiter(key_func=get_remote_address)


# In-memory cache fallback
_memory_cache = {}

def _get_redis():
    """Get Redis client if available."""
    try:
        import redis
        from config.settings import REDIS_URL
        return redis.from_url(REDIS_URL, decode_responses=True)
    except:
        return None


def _cache_get(key: str):
    """Get value from Redis cache or in-memory fallback."""
    # Try Redis first
    redis_client = _get_redis()
    if redis_client:
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        except:
            pass
    
    # In-memory fallback
    cached = _memory_cache.get(key)
    if cached:
        val, expiry = cached
        if datetime.now() < expiry:
            return val
        else:
            del _memory_cache[key]
    return None


def _cache_set(key: str, value, ttl: int = 600):
    """Set value in Redis cache or in-memory fallback."""
    # Set in Redis
    redis_client = _get_redis()
    if redis_client:
        try:
            redis_client.setex(key, ttl, json.dumps(value, default=str))
        except:
            pass
    
    # Always set in-memory for fast access/fallback
    expiry = datetime.now() + timedelta(seconds=ttl)
    _memory_cache[key] = (value, expiry)


@router.get("/dashboard", response_model=AnalyticsDashboard, summary="Get complete dashboard data")
async def get_dashboard(
    request: Request,
    search_service: JobSearchService = Depends(search_dep),
    pg: PostgresStorage = Depends(pg_dep)
):
    """Single endpoint with all dashboard data to avoid waterfall loading."""
    # Try cache first
    cached = _cache_get("analytics:dashboard")
    if cached:
        return AnalyticsDashboard(**cached)

    # Get raw analytics
    import asyncio
    
    # Run independent heavy tasks in parallel
    # Note: search_service.get_analytics and other methods might not be fully async,
    # but using gather prepares the structure for future async storage layer
    # and handles independent processing blocks.
    
    raw = search_service.get_analytics()
    total_jobs = raw["total_jobs"]

    # Wrap sync calls in threads or just run them if they are fast enough for now
    # Ideally, storage methods should be async.
    # For now, we perform the computation blocks independently.
    
    last_scraped = _get_last_scraped_at(pg)
    seniority = _get_seniority_breakdown(pg, total_jobs)
    
    # Build summary
    summary = SummaryResponse(
        total_jobs=total_jobs,
        fresher_friendly=raw["fresher_friendly"],
        remote_jobs=raw["remote_jobs"],
        portals_tracked=len(raw.get("portal_distribution", [])),
        domains_covered=len(raw.get("domain_distribution", [])),
        last_scraped_at=last_scraped
    )

    # Domain distribution with percentages
    domain_distribution = []
    for entry in raw.get("domain_distribution", []):
        percentage = round((entry["count"] / total_jobs * 100), 1) if total_jobs > 0 else 0.0
        domain_distribution.append(DomainDistribution(
            domain=entry["domain"],
            count=entry["count"],
            percentage=percentage
        ))

    # Top skills
    top_skills = raw.get("top_skills", [])

    # Portal distribution with percentages
    portal_distribution = []
    for entry in raw.get("portal_distribution", []):
        percentage = round((entry["count"] / total_jobs * 100), 1) if total_jobs > 0 else 0.0
        portal_distribution.append(PortalDistribution(
            portal=entry["portal"],
            display_name=entry.get("display_name", entry["portal"]),
            count=entry["count"],
            percentage=percentage
        ))

    # Remote vs onsite
    remote = raw.get("remote_jobs", 0)
    onsite = total_jobs - remote
    remote_percentage = round((remote / total_jobs * 100), 1) if total_jobs > 0 else 0.0
    remote_vs_onsite = RemoteVsOnsite(
        remote=remote,
        onsite=onsite,
        remote_percentage=remote_percentage
    )

    dashboard = AnalyticsDashboard(
        summary=summary,
        domain_distribution=domain_distribution,
        top_skills=top_skills,
        seniority_breakdown=seniority,
        portal_distribution=portal_distribution,
        remote_vs_onsite=remote_vs_onsite,
        source=raw.get("source", "pg")
    )

    # Cache for 10 minutes
    _cache_set("analytics:dashboard", dashboard.model_dump(), ttl=600)

    return dashboard


@router.get("/summary", response_model=SummaryResponse, summary="Get summary statistics")
async def get_summary(
    request: Request,
    search_service: JobSearchService = Depends(search_dep),
    pg: PostgresStorage = Depends(pg_dep)
):
    """Get summary statistics subset of dashboard."""
    cached = _cache_get("analytics:dashboard")
    if cached:
        return SummaryResponse(**cached["summary"])

    # Compute fresh if not cached
    dashboard = await get_dashboard(request, search_service, pg)
    return dashboard.summary


@router.get("/top-skills", summary="Get top skills by frequency")
async def get_top_skills(
    request: Request,
    search_service: JobSearchService = Depends(search_dep),
    limit: int = Query(20, ge=1, le=100, description="Maximum skills to return")
):
    """Get top skills by frequency."""
    cache_key = f"analytics:top_skills:{limit}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    analytics = search_service.get_analytics()
    skills = analytics.get("top_skills", [])[:limit]

    _cache_set(cache_key, skills, ttl=600)
    return skills


@router.get("/domain-distribution", response_model=List[DomainDistribution], summary="Get domain distribution")
async def get_domain_distribution(
    request: Request,
    search_service: JobSearchService = Depends(search_dep)
):
    """Get job distribution by domain with percentages."""
    cached = _cache_get("analytics:domain_dist")
    if cached:
        return [DomainDistribution(**item) for item in cached]

    raw = search_service.get_analytics()
    total_jobs = raw["total_jobs"]

    distribution = []
    for entry in raw.get("domain_distribution", []):
        percentage = round((entry["count"] / total_jobs * 100), 1) if total_jobs > 0 else 0.0
        distribution.append(DomainDistribution(
            domain=entry["domain"],
            count=entry["count"],
            percentage=percentage
        ))

    cache_data = [item.model_dump() for item in distribution]
    _cache_set("analytics:domain_dist", cache_data, ttl=600)

    return distribution


@router.get("/seniority-breakdown", response_model=List[SeniorityBreakdown], summary="Get seniority breakdown")
async def get_seniority_breakdown_endpoint(
    request: Request,
    pg: PostgresStorage = Depends(pg_dep)
):
    """Get job distribution by seniority level."""
    cached = _cache_get("analytics:seniority")
    if cached:
        return [SeniorityBreakdown(**item) for item in cached]

    breakdown = _get_seniority_breakdown(pg)
    cache_data = [item.model_dump() for item in breakdown]
    _cache_set("analytics:seniority", cache_data, ttl=600)

    return breakdown


@router.get("/portal-distribution", response_model=List[PortalDistribution], summary="Get portal distribution")
async def get_portal_distribution(
    request: Request,
    search_service: JobSearchService = Depends(search_dep)
):
    """Get job distribution by portal with percentages."""
    cached = _cache_get("analytics:portal_dist")
    if cached:
        return [PortalDistribution(**item) for item in cached]

    raw = search_service.get_analytics()
    total_jobs = raw["total_jobs"]

    distribution = []
    for entry in raw.get("portal_distribution", []):
        percentage = round((entry["count"] / total_jobs * 100), 1) if total_jobs > 0 else 0.0
        distribution.append(PortalDistribution(
            portal=entry["portal"],
            display_name=entry.get("display_name", entry["portal"]),
            count=entry["count"],
            percentage=percentage
        ))

    cache_data = [item.model_dump() for item in distribution]
    _cache_set("analytics:portal_dist", cache_data, ttl=600)

    return distribution


@router.get("/salary-ranges", response_model=List[SalaryRange], summary="Get salary ranges by domain")
async def get_salary_ranges(
    request: Request,
    pg: PostgresStorage = Depends(pg_dep)
):
    """Get average salary ranges by domain."""
    cached = _cache_get("analytics:salary_ranges")
    if cached:
        return [SalaryRange(**item) for item in cached]

    try:
        with pg.get_session() as session:
            from sqlalchemy import text
            result = session.execute(text("""
                SELECT domain,
                       AVG(salary_min) as avg_min,
                       AVG(salary_max) as avg_max,
                       salary_currency
                FROM jobs
                WHERE is_active = true
                  AND salary_disclosed = true
                  AND salary_min IS NOT NULL
                GROUP BY domain, salary_currency
                ORDER BY avg_min DESC NULLS LAST
            """)).fetchall()

            ranges = []
            for row in result:
                ranges.append(SalaryRange(
                    domain=row.domain,
                    avg_min=float(row.avg_min) if row.avg_min else None,
                    avg_max=float(row.avg_max) if row.avg_max else None,
                    currency=row.salary_currency or "INR"
                ))

            cache_data = [item.model_dump() for item in ranges]
            _cache_set("analytics:salary_ranges", cache_data, ttl=600)

            return ranges
    except Exception:
        return []


@router.get("/trending-skills", response_model=List[TrendingSkill], summary="Get trending skills")
async def get_trending_skills(
    request: Request,
    pg: PostgresStorage = Depends(pg_dep)
):
    """Get trending skills comparing this week vs last week."""
    cached = _cache_get("analytics:trending")
    if cached:
        return [TrendingSkill(**item) for item in cached]

    try:
        with pg.get_session() as session:
            from sqlalchemy import text

            # This week
            this_week_result = session.execute(text("""
                SELECT skill, COUNT(*) as cnt
                FROM jobs, jsonb_array_elements_text(skills::jsonb) AS skill
                WHERE scraped_at >= NOW() - INTERVAL '7 days'
                  AND is_active = true
                GROUP BY skill ORDER BY cnt DESC LIMIT 20
            """)).fetchall()

            # Last week
            last_week_result = session.execute(text("""
                SELECT skill, COUNT(*) as cnt
                FROM jobs, jsonb_array_elements_text(skills::jsonb) AS skill
                WHERE scraped_at BETWEEN NOW()-INTERVAL '14 days' AND NOW()-INTERVAL '7 days'
                  AND is_active = true
                GROUP BY skill ORDER BY cnt DESC LIMIT 20
            """)).fetchall()

            # Build lookup for last week
            last_week_counts = {row.skill: row.cnt for row in last_week_result}

            trending = []
            for row in this_week_result:
                this_week = row.cnt
                last_week = last_week_counts.get(row.skill, 0)

                # Calculate percentage change
                if last_week > 0:
                    change_pct = round(((this_week - last_week) / last_week) * 100, 1)
                else:
                    change_pct = 0.0

                trending.append(TrendingSkill(
                    skill=row.skill,
                    count_this_week=this_week,
                    count_last_week=last_week,
                    change_pct=change_pct
                ))

            # If less than 7 days of data, return top skills with zero last week
            if not this_week_result:
                # Get overall top skills as fallback
                stats = pg.get_stats()
                for skill_data in stats.get("top_skills", [])[:10]:
                    trending.append(TrendingSkill(
                        skill=skill_data["skill"],
                        count_this_week=skill_data["count"],
                        count_last_week=0,
                        change_pct=0.0
                    ))

            cache_data = [item.model_dump() for item in trending]
            _cache_set("analytics:trending", cache_data, ttl=300)  # 5 minutes

            return trending
    except Exception:
        return []


@router.get("/remote-vs-onsite", response_model=RemoteVsOnsite, summary="Get remote vs onsite breakdown")
async def get_remote_vs_onsite(
    request: Request,
    search_service: JobSearchService = Depends(search_dep)
):
    """Get remote vs onsite job breakdown."""
    cached = _cache_get("analytics:remote_onsite")
    if cached:
        return RemoteVsOnsite(**cached)

    raw = search_service.get_analytics()
    total_jobs = raw["total_jobs"]
    remote = raw.get("remote_jobs", 0)
    onsite = total_jobs - remote
    remote_percentage = round((remote / total_jobs * 100), 1) if total_jobs > 0 else 0.0

    result = RemoteVsOnsite(
        remote=remote,
        onsite=onsite,
        remote_percentage=remote_percentage
    )

    _cache_set("analytics:remote_onsite", result.model_dump(), ttl=600)

    return result


def _get_last_scraped_at(pg) -> Optional[datetime]:
    """Get the most recent scraped_at timestamp."""
    try:
        with pg.get_session() as session:
            from sqlalchemy import text
            result = session.execute(text("""
                SELECT MAX(scraped_at) as max_scraped_at FROM jobs WHERE is_active = true
            """)).fetchone()
            return result.max_scraped_at if result else None
    except:
        return None


def _get_seniority_breakdown(pg: PostgresStorage, total_jobs: Optional[int] = None) -> List[SeniorityBreakdown]:
    """Get seniority breakdown with percentages."""
    try:
        with pg.get_session() as session:
            from sqlalchemy import text
            result = session.execute(text("""
                SELECT seniority, COUNT(*) as count
                FROM jobs
                WHERE is_active = true
                GROUP BY seniority
                ORDER BY count DESC
            """)).fetchall()

            if total_jobs is None:
                total_jobs = sum(row.count for row in result)

            breakdown = []
            for row in result:
                percentage = round((row.count / total_jobs * 100), 1) if total_jobs > 0 else 0.0
                breakdown.append(SeniorityBreakdown(
                    seniority=row.seniority or "Unknown",
                    count=row.count,
                    percentage=percentage
                ))

            return breakdown
    except:
        return []