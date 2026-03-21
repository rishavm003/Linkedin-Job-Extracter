"""
RapidAPI scraper — uses RapidAPI job search endpoints.
Requires RAPIDAPI_KEY from environment.
Uses LinkedIn Data API and Job Search API from RapidAPI marketplace.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger
from config.settings import RAPIDAPI_KEY

# RapidAPI endpoints for job search
RAPIDAPI_LINKEDIN_JOBS = "https://linkedin-data-scraper.p.rapidapi.com/search_jobs"
RAPIDAPI_JSEARCH = "https://jsearch.p.rapidapi.com/search"

SEARCH_QUERIES = [
    "fresher",
    "entry level",
    "junior",
    "intern",
    "trainee",
    "graduate",
    "0-1 years",
    "software engineer fresher",
    "data analyst fresher",
    "web developer fresher",
]


class RapidAPIScraper(BaseScraper):
    portal_name = "rapidapi"
    portal_display = "RapidAPI Jobs"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 100) -> list[RawJob]:
        jobs: list[RawJob] = []
        
        if not RAPIDAPI_KEY:
            logger.warning("[RapidAPI] Missing RAPIDAPI_KEY. Skipping.")
            return jobs
        
        queries = keywords if keywords else SEARCH_QUERIES
        
        # Try JSearch API first (more reliable for fresher jobs)
        for query in queries[:5]:  # Limit queries to avoid rate limits
            if len(jobs) >= max_jobs:
                break
            
            logger.info(f"[RapidAPI] Searching: {query}")
            
            try:
                headers = {
                    "X-RapidAPI-Key": RAPIDAPI_KEY,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
                }
                
                params = {
                    "query": f"{query} in India",
                    "page": "1",
                    "num_pages": "1",
                    "date_posted": "month",
                }
                
                client = await self._get_client()
                await self._polite_delay()
                
                response = await client.get(
                    RAPIDAPI_JSEARCH,
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                results = data.get("data", [])
                logger.info(f"[RapidAPI] Found {len(results)} jobs for '{query}'")
                
                for item in results:
                    if len(jobs) >= max_jobs:
                        break
                    
                    try:
                        # Extract job details
                        job_title = item.get("job_title", "")
                        employer = item.get("employer_name", "Unknown")
                        
                        # Skip non-fresher jobs
                        job_title_lower = job_title.lower()
                        if not any(kw.lower() in job_title_lower or kw.lower() in employer.lower() 
                                  for kw in ["fresher", "entry", "junior", "intern", "trainee", "graduate"]):
                            continue
                        
                        job = RawJob(
                            source_portal=self.portal_name,
                            source_url=item.get("job_apply_link", "") or item.get("job_google_link", ""),
                            title=job_title.strip(),
                            company=employer.strip(),
                            location=item.get("job_location", "India"),
                            description=item.get("job_description", "")[:1000],  # Truncate long descriptions
                            salary_raw=item.get("job_salary", None),
                            job_type=item.get("job_employment_type", "Full-time"),
                            posted_date_raw=item.get("job_posted_at_datetime_utc", None),
                            raw_tags=item.get("job_required_skills", []) or [],
                        )
                        jobs.append(job)
                    except Exception as e:
                        logger.warning(f"[RapidAPI] Skipping malformed job: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"[RapidAPI] Failed to fetch '{query}': {e}")
                continue
        
        logger.info(f"[RapidAPI] ✓ Total scraped: {len(jobs)} jobs")
        return jobs
    
    async def _get_client(self):
        """Override to add RapidAPI headers to all requests."""
        if self._http is None or self._http.is_closed:
            import httpx
            self._http = httpx.AsyncClient(
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                },
                follow_redirects=True,
            )
        return self._http
