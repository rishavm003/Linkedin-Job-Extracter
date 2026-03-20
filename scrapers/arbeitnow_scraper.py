"""
Arbeitnow scraper — completely free public API, no auth needed.
Has many remote-friendly and entry-level jobs globally + India.
API: https://www.arbeitnow.com/api/job-board-api
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger

ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"


class ArbeitnowScraper(BaseScraper):
    portal_name = "arbeitnow"
    portal_display = "Arbeitnow"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 150) -> list[RawJob]:
        jobs: list[RawJob] = []
        page = 1

        while len(jobs) < max_jobs:
            logger.info(f"[Arbeitnow] Fetching page {page}...")
            try:
                data = await self._fetch_json(ARBEITNOW_API, params={"page": page})
            except Exception as e:
                logger.error(f"[Arbeitnow] Page {page} failed: {e}")
                break

            items = data.get("data", [])
            if not items:
                logger.info("[Arbeitnow] No more pages.")
                break

            for item in items:
                if len(jobs) >= max_jobs:
                    break

                title = item.get("title", "") or ""
                company = item.get("company_name", "") or ""
                description = item.get("description", "") or ""
                tags = item.get("tags", []) or []

                if not title or not company:
                    continue

                if keywords:
                    combined = (title + description).lower()
                    if not any(kw.lower() in combined for kw in keywords):
                        continue

                try:
                    job = RawJob(
                        source_portal=self.portal_name,
                        source_url=item.get("url", ""),
                        title=title.strip(),
                        company=company.strip(),
                        location=item.get("location", "Remote"),
                        description=description,
                        salary_raw=None,
                        job_type="Full-time" if not item.get("remote", False) else "Remote",
                        posted_date_raw=item.get("created_at", None),
                        raw_tags=tags,
                    )
                    jobs.append(job)
                except Exception as e:
                    logger.warning(f"[Arbeitnow] Skipping job: {e}")

            # Check if there are more pages
            meta = data.get("meta", {})
            links = data.get("links", {})
            if not links.get("next"):
                break
            page += 1

        logger.info(f"[Arbeitnow] ✓ Total scraped: {len(jobs)} jobs")
        return jobs
