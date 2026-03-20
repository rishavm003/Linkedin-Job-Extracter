"""
LinkedIn public job search scraper.
Uses Playwright on the /jobs/search endpoint — NO login required.
Only scrapes what is publicly visible without authentication.
"""
from __future__ import annotations
import re
import asyncio
import urllib.parse
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from utils.models import RawJob
from utils.logger import logger

BASE_URL = "https://www.linkedin.com/jobs/search"

# Fresher-focused search queries for LinkedIn
SEARCH_QUERIES = [
    ("fresher software developer", "India"),
    ("entry level data science", "India"),
    ("junior python developer", "India"),
    ("fresher web developer", "India"),
    ("graduate trainee", "India"),
    ("junior developer remote", ""),
]


class LinkedInScraper(BaseScraper):
    portal_name = "linkedin"
    portal_display = "LinkedIn"

    async def scrape(self, keywords: list[str] = None, max_jobs: int = 80) -> list[RawJob]:
        jobs: list[RawJob] = []

        queries = []
        if keywords:
            for kw in keywords:
                queries.append((kw, "India"))
        else:
            queries = SEARCH_QUERIES

        for query, location in queries:
            if len(jobs) >= max_jobs:
                break

            params = {
                "keywords": query,
                "location": location,
                "f_E": "1,2",     # Entry-level + Internship experience levels
                "sortBy": "DD",   # Most recent first
                "position": 1,
                "pageNum": 0,
            }
            url = BASE_URL + "?" + urllib.parse.urlencode(params)
            logger.info(f"[LinkedIn] Searching: '{query}' in '{location}'")

            try:
                html = await self._render_page(
                    url=url,
                    wait_selector=".job-search-card, .base-card"
                )
            except Exception as e:
                logger.error(f"[LinkedIn] Failed to render {url}: {e}")
                continue

            soup = BeautifulSoup(html, "lxml")
            cards = (
                soup.select(".job-search-card") or
                soup.select(".base-card") or
                soup.select("[data-entity-urn]")
            )

            logger.info(f"[LinkedIn] {len(cards)} cards for '{query}'")

            for card in cards:
                if len(jobs) >= max_jobs:
                    break
                try:
                    job = self._parse_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"[LinkedIn] Parse error: {e}")

            # Polite wait between searches
            await asyncio.sleep(4)

        logger.info(f"[LinkedIn] ✓ Total scraped: {len(jobs)} jobs")
        return jobs

    def _parse_card(self, card) -> RawJob | None:
        # Title + apply URL
        title_el = (
            card.select_one("h3.base-search-card__title") or
            card.select_one(".job-search-card__title") or
            card.select_one("h3 a")
        )
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        link_el = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
        apply_url = link_el["href"].split("?")[0] if link_el else ""
        if not apply_url:
            return None

        # Company
        company_el = (
            card.select_one("h4.base-search-card__subtitle") or
            card.select_one(".job-search-card__subtitle")
        )
        company = company_el.get_text(strip=True) if company_el else "Unknown"

        # Location
        loc_el = (
            card.select_one(".job-search-card__location") or
            card.select_one(".base-search-card__metadata span:first-child")
        )
        location = loc_el.get_text(strip=True) if loc_el else "India"

        # Date
        date_el = card.select_one("time")
        posted_raw = date_el.get("datetime") if date_el else None

        # Description not available in list view — use title + company as placeholder
        description = f"{title} at {company}. Location: {location}."

        return RawJob(
            source_portal=self.portal_name,
            source_url=apply_url,
            title=title,
            company=company,
            location=location,
            description=description,
            job_type="Full-time",
            posted_date_raw=posted_raw,
        )
