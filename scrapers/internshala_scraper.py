"""
Internshala scraper — India's #1 internship & fresher jobs portal.
Uses Playwright because the site is React-rendered.
Scrapes: internships + fresher jobs section.
"""
from __future__ import annotations
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger

BASE_URL = "https://internshala.com"

# Internshala search paths for freshers
SEARCH_PATHS = [
    "/internships",
    "/jobs/fresher-jobs",
    "/jobs/work-from-home-jobs",
]


class IntershalaScraper(BaseScraper):
    portal_name = "internshala"
    portal_display = "Internshala"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 100) -> list[RawJob]:
        jobs: list[RawJob] = []

        for path in SEARCH_PATHS:
            if len(jobs) >= max_jobs:
                break

            url = BASE_URL + path
            logger.info(f"[Internshala] Fetching {url}")

            try:
                html = await self._render_page(
                    url=url,
                    wait_selector=".internship_meta, .job-internship-name, .individual_internship"
                )
            except Exception as e:
                logger.error(f"[Internshala] Failed to render {url}: {e}")
                continue

            soup = BeautifulSoup(html, "lxml")
            listings = soup.select(".individual_internship, .internship-list-container .internship_meta")

            if not listings:
                # Try alternate selectors that Internshala uses
                listings = soup.select("[class*='internship']")

            logger.info(f"[Internshala] Found {len(listings)} listings on {path}")

            for card in listings:
                if len(jobs) >= max_jobs:
                    break
                try:
                    job = self._parse_card(card, path)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"[Internshala] Card parse error: {e}")

        logger.info(f"[Internshala] ✓ Total scraped: {len(jobs)} jobs")
        return jobs

    def _parse_card(self, card, path: str) -> RawJob | None:
        # Title
        title_el = (
            card.select_one(".job-internship-name a") or
            card.select_one("h3 a") or
            card.select_one(".profile a")
        )
        title = title_el.get_text(strip=True) if title_el else None
        if not title:
            return None

        # Company
        company_el = (
            card.select_one(".company-name") or
            card.select_one(".company_name") or
            card.select_one("p.company-name")
        )
        company = company_el.get_text(strip=True) if company_el else "Unknown"

        # URL
        link_el = card.select_one("a[href*='/internship/'], a[href*='/job/']")
        href = link_el["href"] if link_el and link_el.get("href") else ""
        apply_url = BASE_URL + href if href.startswith("/") else href

        # Location
        loc_el = (
            card.select_one(".location_link") or
            card.select_one(".location a") or
            card.select_one("[class*='location']")
        )
        location = loc_el.get_text(strip=True) if loc_el else "India"

        # Stipend / salary
        stipend_el = card.select_one(".stipend, .salary")
        salary_raw = stipend_el.get_text(strip=True) if stipend_el else None

        # Job type
        job_type = "Internship" if "/internships" in path else "Full-time"

        # Duration / description snippets
        duration_el = card.select_one(".internship-other-details, .other-info")
        description = duration_el.get_text(separator=" ", strip=True) if duration_el else ""

        # Posted date
        posted_el = card.select_one(".status-inactive, .posted_by_time")
        posted_raw = posted_el.get_text(strip=True) if posted_el else None

        return RawJob(
            source_portal=self.portal_name,
            source_url=apply_url or BASE_URL + path,
            title=title,
            company=company,
            location=location,
            description=description,
            salary_raw=salary_raw,
            job_type=job_type,
            posted_date_raw=posted_raw,
        )
