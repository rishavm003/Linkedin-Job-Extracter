"""
RemoteOK scraper — free public JSON API.
No auth needed. Returns JSON array of job objects.
API: https://remoteok.com/api
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger

REMOTEOK_API = "https://remoteok.com/api"

FRESHER_TAGS = {
    "junior", "entry", "entry-level", "intern", "internship",
    "graduate", "fresher", "trainee", "associate", "beginner",
}


class RemoteOKScraper(BaseScraper):
    portal_name = "remoteok"
    portal_display = "RemoteOK"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 150) -> list[RawJob]:
        jobs: list[RawJob] = []
        logger.info("[RemoteOK] Fetching jobs from API...")

        try:
            # RemoteOK returns an array; first item is a legal notice dict
            data = await self._fetch_json(REMOTEOK_API)
        except Exception as e:
            logger.error(f"[RemoteOK] API fetch failed: {e}")
            return jobs

        if not isinstance(data, list) or len(data) < 2:
            logger.warning("[RemoteOK] Unexpected API response format")
            return jobs

        items = data[1:]  # skip the legal notice
        logger.info(f"[RemoteOK] {len(items)} total jobs fetched")

        for item in items:
            if len(jobs) >= max_jobs:
                break
            if not isinstance(item, dict):
                continue

            tags: list[str] = item.get("tags", []) or []
            tags_lower = {t.lower() for t in tags}

            # For freshers: prioritise jobs with junior/entry tags
            # but don't strictly filter — let NLP decide seniority
            title = item.get("position", "") or ""
            company = item.get("company", "") or ""
            description = item.get("description", "") or ""

            if not title or not company:
                continue

            # Light keyword filter
            if keywords:
                combined = (title + description).lower()
                if not any(kw.lower() in combined for kw in keywords):
                    # Still include if it has fresher-friendly tags
                    if not tags_lower.intersection(FRESHER_TAGS):
                        continue

            try:
                job = RawJob(
                    source_portal=self.portal_name,
                    source_url=f"https://remoteok.com{item.get('url', '')}",
                    title=title.strip(),
                    company=company.strip(),
                    location=item.get("location", "Remote") or "Remote",
                    description=description,
                    salary_raw=item.get("salary", None),
                    job_type="Full-time",
                    posted_date_raw=item.get("date", None),
                    raw_tags=tags,
                )
                jobs.append(job)
            except Exception as e:
                logger.warning(f"[RemoteOK] Skipping malformed job: {e}")
                continue

        logger.info(f"[RemoteOK] ✓ Total scraped: {len(jobs)} jobs")
        return jobs
