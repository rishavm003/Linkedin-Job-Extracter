"""
Adzuna scraper — uses Adzuna API for job search.
Requires ADZUNA_APP_ID and ADZUNA_APP_KEY from environment.
API docs: https://developer.adzuna.com/
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger
from config.settings import ADZUNA_APP_ID, ADZUNA_APP_KEY

ADZUNA_API = "https://api.adzuna.com/v1/api/jobs/in/search/1"

# Job categories to search for fresher roles
SEARCH_QUERIES = [
    "fresher software",
    "entry level developer",
    "junior engineer",
    "graduate trainee",
    "intern software",
    "0-1 years experience",
    "python fresher",
    "java fresher",
    "data science fresher",
    "web developer fresher",
]


class AdzunaScraper(BaseScraper):
    portal_name = "adzuna"
    portal_display = "Adzuna"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 100) -> list[RawJob]:
        jobs: list[RawJob] = []
        
        if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
            logger.warning("[Adzuna] Missing ADZUNA_APP_ID or ADZUNA_APP_KEY. Skipping.")
            return jobs
        
        # Use provided keywords or default search queries
        queries = keywords if keywords else SEARCH_QUERIES
        
        for query in queries:
            if len(jobs) >= max_jobs:
                break
            
            logger.info(f"[Adzuna] Searching: {query}")
            
            try:
                params = {
                    "app_id": ADZUNA_APP_ID,
                    "app_key": ADZUNA_APP_KEY,
                    "what": query,
                    "where": "India",
                    "max_days_old": 30,
                    "results_per_page": 20,
                }
                
                data = await self._fetch_json(ADZUNA_API, params=params)
                results = data.get("results", [])
                
                logger.info(f"[Adzuna] Found {len(results)} jobs for '{query}'")
                
                for item in results:
                    if len(jobs) >= max_jobs:
                        break
                    
                    try:
                        job = RawJob(
                            source_portal=self.portal_name,
                            source_url=item.get("redirect_url", "") or item.get("url", ""),
                            title=item.get("title", "").strip(),
                            company=item.get("company", {}).get("display_name", "Unknown").strip(),
                            location=item.get("location", {}).get("display_name", "India"),
                            description=item.get("description", ""),
                            salary_raw=self._format_salary(item.get("salary_is_predicted"), 
                                                             item.get("salary_min"), 
                                                             item.get("salary_max")),
                            job_type=item.get("contract_type", "Full-time"),
                            posted_date_raw=item.get("created_at", None),
                            raw_tags=item.get("category", {}).get("tag", []),
                        )
                        jobs.append(job)
                    except Exception as e:
                        logger.warning(f"[Adzuna] Skipping malformed job: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"[Adzuna] Failed to fetch '{query}': {e}")
                continue
        
        logger.info(f"[Adzuna] ✓ Total scraped: {len(jobs)} jobs")
        return jobs
    
    def _format_salary(self, is_predicted: bool, min_sal: float, max_sal: float) -> str:
        """Format salary information."""
        if not min_sal and not max_sal:
            return None
        
        prefix = "Est. " if is_predicted else ""
        if min_sal and max_sal:
            return f"{prefix}₹{min_sal:,.0f} - ₹{max_sal:,.0f}"
        elif min_sal:
            return f"{prefix}From ₹{min_sal:,.0f}"
        elif max_sal:
            return f"{prefix}Up to ₹{max_sal:,.0f}"
        return None
