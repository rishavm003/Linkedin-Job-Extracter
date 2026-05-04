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
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'apps', 'worker'))

from libs.core.config import (
    SCRAPER_DELAY_MIN, SCRAPER_DELAY_MAX,
    MAX_RETRIES, REQUEST_TIMEOUT, PLAYWRIGHT_HEADLESS, PLAYWRIGHT_SLOW_MO
)
from libs.core.models import RawJob
from libs.core.logger import logger


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

    # ── Playwright helpers ────────────────────────────────────────────────────
    _pw = None
    _browser = None
    _context = None

    async def _get_browser_context(self):
        """Get or create a persistent browser context for this scraper instance."""
        if self._context:
            return self._context

        from playwright.async_api import async_playwright
        self._pw = await async_playwright().start()
        
        # Resource-saving launch arguments
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
            "--disable-blink-features=AutomationControlled",
        ]
        
        self._browser = await self._pw.chromium.launch(
            headless=PLAYWRIGHT_HEADLESS,
            args=launch_args,
        )
        
        self._context = await self._browser.new_context(
            user_agent=ua.random,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        
        # Block images and other heavy resources to save memory/CPU
        await self._context.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,otf,ttf,eot,mp4,webm,ogg}", 
                                  lambda route: route.abort())
        
        # Mask automation signals
        await self._context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        return self._context

    async def _render_page(self, url: str, wait_selector: str = None) -> str:
        """
        Use Playwright to render a JS-heavy page and return HTML.
        Reuses the browser context if available.
        """
        ctx = await self._get_browser_context()
        page = await ctx.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=10000)
                except Exception:
                    logger.warning(f"[{self.portal_name}] Selector '{wait_selector}' not found on {url}")
            
            if PLAYWRIGHT_SLOW_MO:
                await page.wait_for_timeout(PLAYWRIGHT_SLOW_MO)
                
            html = await page.content()
            return html
        finally:
            await page.close()

    # ── Utilities ─────────────────────────────────────────────────────────────

    async def _polite_delay(self):
        """Sleep a random duration to avoid rate limiting."""
        delay = random.uniform(SCRAPER_DELAY_MIN, SCRAPER_DELAY_MAX)
        await asyncio.sleep(delay)

    async def close(self):
        """Cleanup HTTP and Browser resources."""
        if self._http and not self._http.is_closed:
            await self._http.aclose()
        
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()

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
