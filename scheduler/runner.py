"""
Scheduler — runs the full scrape → NLP → save pipeline on a cron interval.
Uses APScheduler. Can also be triggered manually via CLI.
"""
from __future__ import annotations
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rich.console import Console
from rich.table import Table

from scrapers.orchestrator import ScraperOrchestrator
from nlp.pipeline import NLPPipeline
from storage.json_storage import JSONStorage
from config.settings import SCRAPE_INTERVAL_HOURS
from utils.logger import logger

console = Console()


async def run_pipeline(
    portals: list[str] = None,
    max_per_portal: int = 200,
    use_db: bool = False,
) -> dict:
    """
    Full pipeline run:
      1. Scrape all portals
      2. Run NLP pipeline
      3. Save to JSON (and optionally PostgreSQL)

    Returns stats dict.
    """
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    logger.info(f"{'='*60}")
    logger.info(f"[Pipeline] Starting run {run_id}")
    logger.info(f"{'='*60}")

    # ── Step 1: Scrape ────────────────────────────────────────────────────────
    orchestrator = ScraperOrchestrator(max_per_portal=max_per_portal, portals=portals)
    raw_jobs = await orchestrator.run()

    if not raw_jobs:
        logger.warning("[Pipeline] No jobs scraped — aborting run.")
        return {"run_id": run_id, "scraped": 0, "processed": 0, "saved": 0}

    # ── Step 2: NLP processing ────────────────────────────────────────────────
    nlp = NLPPipeline(use_multiprocessing=len(raw_jobs) > 50)
    processed_jobs = nlp.run(raw_jobs)

    # ── Step 3: Save ──────────────────────────────────────────────────────────
    json_store = JSONStorage()
    json_store.save_raw(raw_jobs, run_id=run_id)
    json_store.save_processed(processed_jobs, run_id=run_id)

    inserted = len(processed_jobs)
    if use_db:
        try:
            from storage.postgres import PostgresStorage
            pg = PostgresStorage()
            pg.create_tables()
            inserted, skipped = pg.save_jobs(processed_jobs)
        except Exception as e:
            logger.error(f"[Pipeline] PostgreSQL save failed: {e}")

    # ── Step 4: Index into Elasticsearch (if available) ───────────────────────
    es_result = {"indexed": 0, "failed": 0}
    try:
        from storage.es_indexer import ElasticsearchIndexer
        es = ElasticsearchIndexer()
        if es.available:
            es_result = es.index_jobs(processed_jobs)
            logger.info(f"[Pipeline] ES indexed: {es_result['indexed']}, failed: {es_result['failed']}")
        else:
            logger.info("[Pipeline] Elasticsearch not available — skipping ES indexing")
    except Exception as e:
        logger.warning(f"[Pipeline] ES indexing failed: {e}")

    stats = json_store.get_stats(processed_jobs)
    stats["run_id"] = run_id
    stats["scraped_raw"] = len(raw_jobs)
    stats["processed"] = len(processed_jobs)
    stats["es_indexed"] = es_result.get("indexed", 0)

    _print_summary(stats)
    return stats


def _print_summary(stats: dict):
    """Pretty-print pipeline run summary using Rich."""
    console.print(f"\n[bold green]✓ Pipeline run complete[/bold green]\n")

    table = Table(title="Run Summary", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Raw scraped", str(stats.get("scraped_raw", "—")))
    table.add_row("After NLP + dedup", str(stats.get("processed", "—")))
    table.add_row("Fresher-friendly", str(stats.get("fresher_friendly", "—")))
    table.add_row("Remote jobs", str(stats.get("remote", "—")))
    table.add_row("ES indexed", str(stats.get("es_indexed", "N/A")))
    console.print(table)

    if stats.get("domain_distribution"):
        dtable = Table(title="Domain Breakdown", show_header=True, header_style="bold magenta")
        dtable.add_column("Domain")
        dtable.add_column("Count", justify="right")
        for domain, count in list(stats["domain_distribution"].items())[:10]:
            dtable.add_row(domain, str(count))
        console.print(dtable)

    if stats.get("top_skills"):
        stable = Table(title="Top Skills", show_header=True, header_style="bold yellow")
        stable.add_column("Skill")
        stable.add_column("Mentions", justify="right")
        for skill, count in list(stats["top_skills"].items())[:10]:
            stable.add_row(skill, str(count))
        console.print(stable)


def run_pipeline_sync(*args, **kwargs):
    """Synchronous wrapper for APScheduler."""
    asyncio.run(run_pipeline(*args, **kwargs))


class PipelineScheduler:
    """Wraps APScheduler to run the pipeline on an interval."""

    def __init__(self, interval_hours: int = SCRAPE_INTERVAL_HOURS, use_db: bool = False):
        self.interval_hours = interval_hours
        self.use_db = use_db
        self._scheduler = BlockingScheduler(timezone="UTC")

    def start(self):
        logger.info(f"[Scheduler] Starting — runs every {self.interval_hours} hour(s)")

        self._scheduler.add_job(
            func=run_pipeline_sync,
            trigger=IntervalTrigger(hours=self.interval_hours),
            kwargs={"use_db": self.use_db},
            id="pipeline_job",
            name="Full scrape + NLP pipeline",
            replace_existing=True,
            next_run_time=datetime.utcnow(),   # run immediately on start
        )
        try:
            self._scheduler.start()
        except KeyboardInterrupt:
            logger.info("[Scheduler] Stopped by user.")
            self._scheduler.shutdown()
