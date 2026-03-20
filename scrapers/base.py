"""
BaseScraper — abstract base class every portal scraper inherits from.

Responsibilities:
  - Shared HTTP session with retry logic and polite delays
  - Playwright browser context for JS-rendered pages
  - Standardised error handling and logging
  - Every scraper MUST implement `scrape()` → list[RawJob]
"""
from __future__ import annotations
import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from fake_useragent import UserAgent

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    SCRAPER_DELAY_MIN, SCRAPER_DELAY_MAX,
    MAX_RETRIES, REQUEST_TIMEOUT, PLAYWRIGHT_HEADLESS, PLAYWRIGHT_SLOW_MO
)
from utils.models import RawJob
from utils.logger import logger


ua = UserAgent()


class BaseScraper(ABC):
    """
    Abstract base. All portal scrapers inherit this.
    """

    portal_name: str = "base"
    portal_display: str = "Unknown Portal"

    def __init__(self):
        self._http: Optional[httpx.AsyncClient] = None

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT,
                headers={
                    "User-Agent": ua.random,
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
                follow_redirects=True,
            )
        return self._http

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def _fetch(self, url: str, params: dict = None) -> httpx.Response:
        client = await self._get_client()
        await self._polite_delay()
        logger.debug(f"[{self.portal_name}] GET {url}")
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response

    async def _fetch_json(self, url: str, params: dict = None) -> dict | list:
        resp = await self._fetch(url, params=params)
        return resp.json()

    # ── Playwright helpers ────────────────────────────────────────────────────

    async def _render_page(self, url: str, wait_selector: str = None) -> str:
        """
        Use Playwright to render a JS-heavy page and return HTML.
        Only called by scrapers that need it (Naukri, LinkedIn, etc.)
        """
        from playwright.async_api import async_playwright
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=PLAYWRIGHT_HEADLESS,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            )
            ctx = await browser.new_context(
                user_agent=ua.random,
                viewport={"width": 1280, "height": 800},
                locale="en-US",
            )
            # Mask automation signals
            await ctx.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            page = await ctx.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=8000)
                except Exception:
                    logger.warning(f"[{self.portal_name}] Selector '{wait_selector}' not found on {url}")
            await page.wait_for_timeout(PLAYWRIGHT_SLOW_MO)
            html = await page.content()
            await browser.close()
            return html

    # ── Utilities ─────────────────────────────────────────────────────────────

    async def _polite_delay(self):
        """Sleep a random duration to avoid rate limiting."""
        delay = random.uniform(SCRAPER_DELAY_MIN, SCRAPER_DELAY_MAX)
        await asyncio.sleep(delay)

    async def close(self):
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    async def scrape(self, keywords: list[str] = None, max_jobs: int = 100) -> list[RawJob]:
        """
        Scrape jobs from the portal.
        keywords: search terms (e.g. ["python fresher", "data science entry level"])
        max_jobs: upper limit for this run
        Returns a list of RawJob objects.
        """
        ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
