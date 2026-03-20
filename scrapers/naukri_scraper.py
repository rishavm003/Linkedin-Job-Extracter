"""
Naukri scraper — India's largest job board.
Uses Playwright (JS-heavy SPA). Targets fresher/0-1yr experience listings.
"""
from __future__ import annotations
import re
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger

BASE_URL = "https://www.naukri.com"

SEARCH_URLS = [
    f"{BASE_URL}/fresher-jobs",
    f"{BASE_URL}/0-to-1-year-experience-jobs",
    f"{BASE_URL}/jobs-in-india?experience=0",
    f"{BASE_URL}/python-jobs-0-to-1-years?experience=0",
    f"{BASE_URL}/data-science-jobs-0-to-1-years?experience=0",
]


class NaukriScraper(BaseScraper):
    portal_name = "naukri"
    portal_display = "Naukri"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 100) -> list[RawJob]:
        jobs: list[RawJob] = []

        for url in SEARCH_URLS:
            if len(jobs) >= max_jobs:
                break

            logger.info(f"[Naukri] Fetching {url}")
            try:
                html = await self._render_page(
                    url=url,
                    wait_selector=".jobTuple, .job-container, article.jobTupleHeader"
                )
            except Exception as e:
                logger.error(f"[Naukri] Failed to render {url}: {e}")
                continue

            soup = BeautifulSoup(html, "lxml")

            # Naukri uses multiple class patterns across versions
            cards = (
                soup.select("article.jobTupleHeader") or
                soup.select(".jobTuple") or
                soup.select("[class*='job-container']") or
                soup.select(".srp-jobtuple-wrapper")
            )
            logger.info(f"[Naukri] Found {len(cards)} job cards on {url}")

            for card in cards:
                if len(jobs) >= max_jobs:
                    break
                try:
                    job = self._parse_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"[Naukri] Card parse error: {e}")

        logger.info(f"[Naukri] ✓ Total scraped: {len(jobs)} jobs")
        return jobs

    def _parse_card(self, card) -> RawJob | None:
        # Title
        title_el = (
            card.select_one("a.title") or
            card.select_one(".jobTupleHeader a") or
            card.select_one("a[href*='job-listings']")
        )
        if not title_el:
            return None
        title = title_el.get_text(strip=True)
        apply_url = title_el.get("href", BASE_URL)

        # Company
        company_el = (
            card.select_one(".companyInfo a") or
            card.select_one(".company-name") or
            card.select_one("[class*='comp-name']")
        )
        company = company_el.get_text(strip=True) if company_el else "Unknown"

        # Location
        loc_el = (
            card.select_one(".location span") or
            card.select_one(".ellipsis.loc") or
            card.select_one("[class*='location']")
        )
        location = loc_el.get_text(strip=True) if loc_el else "India"

        # Experience
        exp_el = card.select_one(".experience span, [class*='experience']")
        exp_text = exp_el.get_text(strip=True) if exp_el else ""

        # Salary
        sal_el = card.select_one(".salary span, [class*='salary']")
        salary_raw = sal_el.get_text(strip=True) if sal_el else None

        # Skills / tags
        skill_els = card.select(".tags li, .skill-container span, [class*='skill'] span")
        tags = [s.get_text(strip=True) for s in skill_els]

        # Description snippet
        desc_el = card.select_one(".job-description, .desc, [class*='description']")
        description = desc_el.get_text(separator=" ", strip=True) if desc_el else " ".join(tags)
        if exp_text:
            description = f"Experience required: {exp_text}. {description}"

        # Posted date
        date_el = card.select_one(".type span:last-child, [class*='time']")
        posted_raw = date_el.get_text(strip=True) if date_el else None

        return RawJob(
            source_portal=self.portal_name,
            source_url=apply_url,
            title=title,
            company=company,
            location=location,
            description=description,
            salary_raw=salary_raw,
            job_type="Full-time",
            posted_date_raw=posted_raw,
            raw_tags=tags,
        )
