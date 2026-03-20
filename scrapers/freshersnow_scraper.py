"""
FreshersNow scraper — dedicated fresher jobs portal for India.
Static HTML, easy to scrape. No JS rendering needed.
"""
from __future__ import annotations
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger

BASE_URL = "https://www.freshersnow.com"
PAGES_TO_SCRAPE = 3

SEARCH_URLS = [
    f"{BASE_URL}/category/government-jobs/",
    f"{BASE_URL}/category/it-jobs/",
    f"{BASE_URL}/category/off-campus-drives/",
    f"{BASE_URL}/category/walk-in-interviews/",
]


class FreshersNowScraper(BaseScraper):
    portal_name = "freshersnow"
    portal_display = "FreshersNow"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 80) -> list[RawJob]:
        jobs: list[RawJob] = []

        for base_url in SEARCH_URLS:
            if len(jobs) >= max_jobs:
                break

            for page in range(1, PAGES_TO_SCRAPE + 1):
                if len(jobs) >= max_jobs:
                    break

                url = f"{base_url}page/{page}/" if page > 1 else base_url
                logger.info(f"[FreshersNow] Fetching {url}")

                try:
                    resp = await self._fetch(url)
                    soup = BeautifulSoup(resp.text, "lxml")
                except Exception as e:
                    logger.error(f"[FreshersNow] Failed: {e}")
                    break

                articles = (
                    soup.select("article.post") or
                    soup.select(".blog-post") or
                    soup.select("div.entry-content")
                )

                if not articles:
                    logger.info(f"[FreshersNow] No articles on page {page}")
                    break

                logger.info(f"[FreshersNow] {len(articles)} articles on page {page}")

                for article in articles:
                    if len(jobs) >= max_jobs:
                        break
                    try:
                        job = self._parse_article(article)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"[FreshersNow] Parse error: {e}")

        logger.info(f"[FreshersNow] ✓ Total scraped: {len(jobs)} jobs")
        return jobs

    def _parse_article(self, article) -> RawJob | None:
        title_el = article.select_one("h2 a, h3 a, .entry-title a")
        if not title_el:
            return None

        title = title_el.get_text(strip=True)
        apply_url = title_el.get("href", BASE_URL)

        # Extract company from title pattern: "Company – Role – Location"
        company = "Multiple Companies"
        if "–" in title:
            parts = title.split("–")
            if len(parts) >= 2:
                company = parts[0].strip()
                title = parts[1].strip()
        elif "|" in title:
            parts = title.split("|")
            company = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else title

        # Description / excerpt
        desc_el = article.select_one(".entry-content p, .entry-summary, .post-excerpt")
        description = desc_el.get_text(separator=" ", strip=True) if desc_el else title

        # Tags
        tag_els = article.select(".tags-links a, .post-tags a")
        tags = [t.get_text(strip=True) for t in tag_els]

        # Date
        date_el = article.select_one("time, .entry-date")
        posted_raw = date_el.get("datetime") or date_el.get_text(strip=True) if date_el else None

        return RawJob(
            source_portal=self.portal_name,
            source_url=apply_url,
            title=title,
            company=company,
            location="India",
            description=description,
            job_type="Full-time",
            posted_date_raw=posted_raw,
            raw_tags=tags,
        )
