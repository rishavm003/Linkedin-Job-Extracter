"""Jobs router - job listing, search, detail endpoints."""
from __future__ import annotations
from typing import Optional, List, Annotated
import sys
import os

# Add parent directory to path to import jobextractor modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import search_dep, pg_dep
from schemas.job_schema import (
    JobSummary, JobDetail, JobListResponse, JobSearchResponse,
    PortalInfo, DomainInfo, SkillInfo, SalarySchema
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
limiter = Limiter(key_func=get_remote_address)


def _to_job_summary(job_dict: dict) -> JobSummary:
    """Convert DB/ES job dict to JobSummary schema."""
    salary = SalarySchema(
        min_value=job_dict.get("salary_min"),
        max_value=job_dict.get("salary_max"),
        currency=job_dict.get("salary_currency"),
        period=job_dict.get("salary_period"),
        is_disclosed=job_dict.get("salary_disclosed", False),
        raw=job_dict.get("salary_raw")
    )
    
    return JobSummary(
        id=job_dict["id"],
        title=job_dict["title"],
        company=job_dict["company"],
        location=job_dict["location"],
        is_remote=job_dict["is_remote"],
        source_portal=job_dict["source_portal"],
        portal_display_name=job_dict.get("portal_display_name", job_dict["source_portal"]),
        apply_url=job_dict["apply_url"],
        job_type=job_dict.get("job_type", "Full-time"),
        seniority=job_dict.get("seniority", "Entry Level"),
        domain=job_dict.get("domain", "Unknown"),
        skills=job_dict.get("skills", []),
        salary=salary,
        posted_at=job_dict.get("posted_at"),
        scraped_at=job_dict["scraped_at"],
        description_summary=job_dict.get("description_summary", ""),
        is_fresher_friendly=job_dict.get("is_fresher_friendly", False),
        requires_experience=job_dict.get("requires_experience")
    )


def _to_job_detail(job_dict: dict, similar_jobs: List[JobSummary] = None) -> JobDetail:
    """Convert DB/ES job dict to JobDetail schema."""
    summary = _to_job_summary(job_dict)
    return JobDetail(
        **summary.model_dump(),
        qualifications=job_dict.get("qualifications", []),
        soft_skills=job_dict.get("soft_skills", []),
        description_clean=job_dict.get("description_clean", ""),
        country=job_dict.get("country"),
        city=job_dict.get("city"),
        fingerprint=job_dict["fingerprint"]
    )


@router.get("", response_model=JobListResponse, summary="List jobs with filters")
async def list_jobs(
    request: Request,
    search_service: Annotated[object, Depends(search_dep)],
    domain: Optional[str] = Query(None, description="Filter by job domain"),
    seniority: Optional[str] = Query(None, description="Filter by seniority level"),
    is_remote: Optional[bool] = Query(None, description="Filter for remote jobs only"),
    portal: Optional[str] = Query(None, description="Filter by source portal"),
    is_fresher: Optional[bool] = Query(None, description="Filter for fresher-friendly jobs"),
    skills: Optional[str] = Query(None, description="Comma-separated skills (e.g. python,react,sql)"),
    salary_min: Optional[float] = Query(None, description="Minimum salary (INR annual)"),
    salary_max: Optional[float] = Query(None, description="Maximum salary (INR annual)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    sort_by: str = Query("scraped_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """List jobs with optional filtering and pagination."""
    # Parse skills
    skills_list = []
    if skills:
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Search with filters
    result = search_service.search(
        query="",  # Empty query for listing
        domain=domain,
        seniority=seniority,
        is_remote=is_remote,
        is_fresher=is_fresher,
        portal=portal,
        skills=skills_list,
        salary_min=salary_min,
        salary_max=salary_max,
        limit=page_size,
        offset=offset
    )
    
    # Convert to schema
    jobs = [_to_job_summary(job) for job in result["hits"]]
    total_pages = (result["total"] + page_size - 1) // page_size
    
    return JobListResponse(
        jobs=jobs,
        total=result["total"],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        source=result["source"]
    )


@router.get("/search", response_model=JobSearchResponse, summary="Search jobs by text")
async def search_jobs(
    search_service: Annotated[object, Depends(search_dep)],
    q: str = Query(..., min_length=2, description="Search query (min 2 characters)"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    is_fresher: Optional[bool] = Query(None, description="Filter for fresher-friendly jobs"),
    is_remote: Optional[bool] = Query(None, description="Filter for remote jobs"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return")
):
    """Search jobs by text query with optional filters."""
    result = search_service.search(
        query=q,
        domain=domain,
        is_fresher=is_fresher,
        is_remote=is_remote,
        limit=limit
    )
    
    jobs = [_to_job_summary(job) for job in result["hits"]]
    
    return JobSearchResponse(
        jobs=jobs,
        total=result["total"],
        query=q,
        source=result["source"]
    )


@router.get("/portals", response_model=List[PortalInfo], summary="Get job portals with counts")
async def get_portals(
    pg: Annotated[object, Depends(pg_dep)]
):
    """Get all portals with job counts."""
    portals = pg.get_portal_stats()
    return portals


@router.get("/domains", response_model=List[DomainInfo], summary="Get job domains with counts")
async def get_domains(
    pg: Annotated[object, Depends(pg_dep)]
):
    """Get all domains with job counts."""
    stats = pg.get_stats()
    
    return [
        DomainInfo(domain=item["domain"], count=item["count"])
        for item in stats.get("domain_distribution", [])
    ]


@router.get("/skills", response_model=List[SkillInfo], summary="Get top skills")
async def get_skills(
    search_service: Annotated[object, Depends(search_dep)],
    limit: int = Query(50, ge=1, le=100, description="Maximum skills to return")
):
    """Get top skills by frequency."""
    analytics = search_service.get_analytics()
    
    skills = analytics.get("top_skills", [])[:limit]
    
    return [
        SkillInfo(skill=skill["skill"], count=skill["count"])
        for skill in skills
    ]


@router.get("/{job_id}", response_model=JobDetail, summary="Get job details")
async def get_job_detail(
    job_id: str,
    pg: Annotated[object, Depends(pg_dep)]
):
    """Get detailed information for a specific job."""
    job = pg.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Get similar jobs from same domain
    similar_jobs = []
    try:
        similar = pg.get_jobs(domain=job.get("domain"), limit=5)
        similar_jobs = [
            _to_job_summary(j) for j in similar 
            if j.get("id") != job_id
        ][:4]  # Max 4 similar jobs
    except Exception:
        pass
    
    return _to_job_detail(job, similar_jobs)
