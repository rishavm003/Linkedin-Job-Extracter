"""
ScraperOrchestrator — runs all portal scrapers concurrently and merges results.
This is the entry point for the ingestion layer.
"""
from __future__ import annotations
import asyncio
from typing import Type
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base import BaseScraper
from scrapers.remotive_scraper import RemotiveScraper
from scrapers.remoteok_scraper import RemoteOKScraper
from scrapers.arbeitnow_scraper import ArbeitnowScraper
from scrapers.internshala_scraper import IntershalaScraper
from scrapers.naukri_scraper import NaukriScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.freshersnow_scraper import FreshersNowScraper
from config.settings import MAX_JOBS_PER_PORTAL, FRESHER_KEYWORDS
from utils.models import RawJob
from utils.logger import logger

# Portal registry — add new scrapers here
PORTAL_SCRAPERS: list[Type[BaseScraper]] = [
    RemotiveScraper,      # API — always reliable, run first
    RemoteOKScraper,      # API — always reliable
    ArbeitnowScraper,     # API — always reliable
    IntershalaScraper,    # Playwright — India internships
    FreshersNowScraper,   # HTTP — India freshers
    NaukriScraper,        # Playwright — India jobs
    LinkedInScraper,      # Playwright — global
]


class ScraperOrchestrator:
    """
    Runs all enabled scrapers and returns a merged deduplicated list of RawJobs.
    API-based scrapers run concurrently; Playwright scrapers run sequentially
    to avoid resource exhaustion.
    """

    def __init__(
        self,
        keywords: list[str] = None,
        max_per_portal: int = MAX_JOBS_PER_PORTAL,
        portals: list[str] = None,         # restrict to specific portals (by name)
    ):
        self.keywords = keywords or FRESHER_KEYWORDS
        self.max_per_portal = max_per_portal
        self.portals = portals             # None = all portals

    async def run(self) -> list[RawJob]:
        api_scrapers = [RemotiveScraper, RemoteOKScraper, ArbeitnowScraper]
        browser_scrapers = [IntershalaScraper, FreshersNowScraper, NaukriScraper, LinkedInScraper]

        if self.portals:
            api_scrapers = [s for s in api_scrapers if s.portal_name in self.portals]
            browser_scrapers = [s for s in browser_scrapers if s.portal_name in self.portals]

        all_jobs: list[RawJob] = []

        # ── API scrapers — run concurrently ───────────────────────────────────
        logger.info(f"[Orchestrator] Running {len(api_scrapers)} API scrapers concurrently...")
        api_tasks = [
            self._run_single(scraper_cls)
            for scraper_cls in api_scrapers
        ]
        api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
        for result in api_results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"[Orchestrator] API scraper error: {result}")

        # ── Browser scrapers — run sequentially to save memory ────────────────
        logger.info(f"[Orchestrator] Running {len(browser_scrapers)} browser scrapers sequentially...")
        for scraper_cls in browser_scrapers:
            try:
                result = await self._run_single(scraper_cls)
                all_jobs.extend(result)
            except Exception as e:
                logger.error(f"[Orchestrator] Browser scraper {scraper_cls.portal_name} error: {e}")

        logger.info(f"[Orchestrator] ✓ Raw total: {len(all_jobs)} jobs before dedup")

        # Basic fingerprint dedup at orchestrator level
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            fp = job.fingerprint
            if fp not in seen:
                seen.add(fp)
                unique_jobs.append(job)

        logger.info(f"[Orchestrator] ✓ After fingerprint dedup: {len(unique_jobs)} jobs")
        return unique_jobs

    async def _run_single(self, scraper_cls: Type[BaseScraper]) -> list[RawJob]:
        async with scraper_cls() as scraper:
            try:
                jobs = await scraper.scrape(
                    keywords=self.keywords,
                    max_jobs=self.max_per_portal,
                )
                logger.info(f"[Orchestrator] {scraper_cls.portal_name}: {len(jobs)} jobs")
                return jobs
            except Exception as e:
                logger.error(f"[Orchestrator] {scraper_cls.portal_name} failed: {e}")
                return []
