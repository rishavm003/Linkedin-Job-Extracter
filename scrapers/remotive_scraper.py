"""
Remotive scraper — uses their FREE public JSON API.
No authentication required. Returns up to 500 remote jobs per category.
API docs: https://remotive.com/api
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger

REMOTIVE_API = "https://remotive.com/api/remote-jobs"

# Map Remotive categories to our job domains
CATEGORY_MAP = {
    "software-dev": "Software Development",
    "customer-support": "Customer Support",
    "design": "UI/UX Design",
    "marketing": "Digital Marketing",
    "sales": "Sales",
    "product": "Product Management",
    "business": "Operations",
    "data": "Data Science & ML",
    "devops": "DevOps & Cloud",
    "finance-legal": "Finance & Accounting",
    "hr": "HR & Recruitment",
    "qa": "Software Development",
    "writing": "Content Writing",
    "all-others": "Other",
}

FRESHER_CATEGORIES = [
    "software-dev", "data", "design", "qa", "writing", "devops"
]


class RemotiveScraper(BaseScraper):
    portal_name = "remotive"
    portal_display = "Remotive"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 200) -> list[RawJob]:
        jobs: list[RawJob] = []

        for category in FRESHER_CATEGORIES:
            if len(jobs) >= max_jobs:
                break

            logger.info(f"[Remotive] Fetching category: {category}")
            try:
                data = await self._fetch_json(
                    REMOTIVE_API,
                    params={"category": category, "limit": 50}
                )
            except Exception as e:
                logger.error(f"[Remotive] Failed to fetch {category}: {e}")
                continue

            raw_jobs = data.get("jobs", [])
            logger.info(f"[Remotive] {len(raw_jobs)} jobs in {category}")

            for item in raw_jobs:
                if len(jobs) >= max_jobs:
                    break

                # Keyword filter — fresher / entry level signals
                if keywords:
                    text = (item.get("title", "") + item.get("description", "")).lower()
                    if not any(kw.lower() in text for kw in keywords):
                        continue

                try:
                    job = RawJob(
                        source_portal=self.portal_name,
                        source_url=item.get("url", ""),
                        title=item.get("title", "").strip(),
                        company=item.get("company_name", "").strip(),
                        location=item.get("candidate_required_location", "Worldwide"),
                        description=item.get("description", ""),
                        salary_raw=item.get("salary", None),
                        job_type=item.get("job_type", "full_time"),
                        posted_date_raw=item.get("publication_date", None),
                        raw_tags=item.get("tags", []),
                    )
                    jobs.append(job)
                except Exception as e:
                    logger.warning(f"[Remotive] Skipping malformed job: {e}")
                    continue

        logger.info(f"[Remotive] ✓ Total scraped: {len(jobs)} jobs")
        return jobs
