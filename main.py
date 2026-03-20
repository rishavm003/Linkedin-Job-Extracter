#!/usr/bin/env python3
"""
Job Extractor — Main entry point.

Usage:
  python main.py run              # run pipeline once now
  python main.py schedule         # run on cron schedule (every 6 hrs)
  python main.py run --portals remotive remoteok
  python main.py run --max 100    # max 100 jobs per portal
  python main.py stats            # show stats from saved data
  python main.py test-scraper remotive   # test one scraper
"""
import asyncio
import argparse
import sys
import os

# Make sure the project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()


def banner():
    console.print(Panel.fit(
        "[bold cyan]Job Extractor Pipeline[/bold cyan]\n"
        "[dim]Multi-portal · NLP-powered · Fresher-focused[/dim]",
        border_style="cyan",
    ))


async def cmd_run(args):
    from scheduler.runner import run_pipeline
    
    # Run alembic migrations before pipeline if using DB
    if args.db:
        import subprocess
        try:
            subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            console.print(f"[yellow]Alembic migration skipped: {e}[/yellow]")
    
    await run_pipeline(
        portals=args.portals or None,
        max_per_portal=args.max,
        use_db=args.db,
    )


async def cmd_test_scraper(args):
    """Quick test for a single scraper — shows first 3 results."""
    portal = args.portal
    scrapers = {
        "remotive": "scrapers.remotive_scraper.RemotiveScraper",
        "remoteok": "scrapers.remoteok_scraper.RemoteOKScraper",
        "arbeitnow": "scrapers.arbeitnow_scraper.ArbeitnowScraper",
        "internshala": "scrapers.internshala_scraper.IntershalaScraper",
        "naukri": "scrapers.naukri_scraper.NaukriScraper",
        "linkedin": "scrapers.linkedin_scraper.LinkedInScraper",
        "freshersnow": "scrapers.freshersnow_scraper.FreshersNowScraper",
    }

    if portal not in scrapers:
        console.print(f"[red]Unknown portal: {portal}[/red]")
        console.print(f"Available: {', '.join(scrapers.keys())}")
        return

    module_path, class_name = scrapers[portal].rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    ScraperClass = getattr(module, class_name)

    console.print(f"[cyan]Testing {portal} scraper...[/cyan]")
    async with ScraperClass() as scraper:
        jobs = await scraper.scrape(max_jobs=5)

    console.print(f"\n[green]Got {len(jobs)} jobs:[/green]")
    for i, job in enumerate(jobs[:3], 1):
        console.print(f"\n[bold]{i}. {job.title}[/bold]")
        console.print(f"   Company : {job.company}")
        console.print(f"   Location: {job.location}")
        console.print(f"   URL     : {job.source_url[:80]}...")
        console.print(f"   Desc    : {job.description[:150]}...")


async def cmd_test_nlp(args):
    """Run NLP extraction on a sample raw job."""
    from utils.models import RawJob
    from nlp.pipeline import NLPPipeline

    sample = RawJob(
        source_portal="test",
        source_url="https://example.com/job/123",
        title="Junior Python Developer (Fresher)",
        company="TechCorp India",
        location="Bangalore, India",
        description="""
        We are looking for a fresher Python developer to join our team.
        
        Required Skills:
        - Python, Django, Flask
        - Basic knowledge of SQL (PostgreSQL / MySQL)
        - Understanding of REST APIs
        - HTML, CSS (bonus)
        
        Qualifications: B.Tech / B.E in Computer Science or related field
        Experience: 0-1 years (freshers welcome)
        Salary: ₹3-5 LPA
        Job Type: Full-time
        
        Good communication skills and team player attitude required.
        """,
        salary_raw="₹3-5 LPA",
        job_type="Full-time",
    )

    pipeline = NLPPipeline(use_multiprocessing=False)
    result = pipeline.process_single(sample)

    if result:
        console.print("\n[bold green]NLP Extraction Result:[/bold green]")
        console.print(f"  Title      : {result.title}")
        console.print(f"  Company    : {result.company}")
        console.print(f"  Domain     : [cyan]{result.domain}[/cyan]")
        console.print(f"  Seniority  : {result.seniority}")
        console.print(f"  Skills     : [yellow]{', '.join(result.skills[:10])}[/yellow]")
        console.print(f"  Quals      : {result.qualifications}")
        console.print(f"  Salary     : {result.salary.raw} → min={result.salary.min_value}, max={result.salary.max_value}")
        console.print(f"  Is Fresher : {'✓' if result.is_fresher_friendly else '✗'}")
        console.print(f"  Is Remote  : {'✓' if result.is_remote else '✗'}")
        console.print(f"  Summary    : {result.description_summary}")
    else:
        console.print("[red]NLP extraction failed.[/red]")


def cmd_stats(args):
    from storage.json_storage import JSONStorage
    store = JSONStorage()
    jobs = store.load_all_processed()
    stats = store.get_stats(jobs)

    if stats["total"] == 0:
        console.print("[yellow]No processed data found. Run the pipeline first.[/yellow]")
        return

    from scheduler.runner import _print_summary
    _print_summary(stats)


def cmd_db_migrate(args):
    """Run alembic upgrade head."""
    import subprocess
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True, text=True)
        console.print("[green]✓ Database migrations applied successfully[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Migration failed: {e.stderr}[/red]")
    except FileNotFoundError:
        console.print("[red]alembic not found. Is it installed?[/red]")


def cmd_db_seed(args):
    """Run seed script."""
    import subprocess
    cmd = ["python", "scripts/seed_db.py"]
    if args.file:
        cmd.extend(["--file", args.file])
    subprocess.run(cmd)


def cmd_db_status(args):
    """Show database status."""
    import subprocess
    try:
        result = subprocess.run(["alembic", "current"], capture_output=True, text=True)
        console.print(f"[cyan]Current migration:[/cyan] {result.stdout.strip()}")
    except Exception:
        console.print("[yellow]Could not get migration status[/yellow]")
    
    try:
        from storage.postgres import PostgresStorage
        pg = PostgresStorage()
        count = pg.get_job_count()
        console.print(f"[cyan]Jobs in database:[/cyan] {count}")
    except Exception as e:
        console.print(f"[yellow]PostgreSQL not available: {e}[/yellow]")


def cmd_es_index(args):
    """Index all processed JSON into ES."""
    console.print("[dim]Indexing processed jobs into Elasticsearch...[/dim]")
    
    import glob
    import json
    from storage.es_indexer import ElasticsearchIndexer
    from utils.models import ProcessedJob
    from datetime import datetime
    
    def parse_datetime(value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return None
        return value
    
    files = glob.glob("data/processed/processed_*.json")
    if not files:
        console.print("[yellow]No processed files found[/yellow]")
        return
    
    all_jobs = []
    for filepath in files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            for item in data:
                if 'posted_at' in item and item['posted_at']:
                    item['posted_at'] = parse_datetime(item['posted_at'])
                if 'scraped_at' in item and item['scraped_at']:
                    item['scraped_at'] = parse_datetime(item['scraped_at'])
                if 'processed_at' in item and item['processed_at']:
                    item['processed_at'] = parse_datetime(item['processed_at'])
                all_jobs.append(ProcessedJob(**item))
        except Exception as e:
            console.print(f"[red]Failed to load {filepath}: {e}[/red]")
    
    try:
        es = ElasticsearchIndexer()
        if not es.available:
            console.print("[red]Elasticsearch not available[/red]")
            return
        result = es.index_jobs(all_jobs)
        console.print(f"[green]✓ Indexed {result['indexed']} jobs, {result['failed']} failed[/green]")
    except Exception as e:
        console.print(f"[red]ES indexing failed: {e}[/red]")


def cmd_es_status(args):
    """Show ES health and job count."""
    from storage.es_indexer import ElasticsearchIndexer
    try:
        es = ElasticsearchIndexer()
        if es.available:
            count = es.get_job_count()
            console.print(f"[green]✓ Elasticsearch connected[/green]")
            console.print(f"[cyan]Jobs in index:[/cyan] {count}")
        else:
            console.print("[red]✗ Elasticsearch not available[/red]")
    except Exception as e:
        console.print(f"[red]ES error: {e}[/red]")


def cmd_search(args):
    """Run a test search."""
    from storage.search import JobSearchService
    
    service = JobSearchService()
    result = service.search(
        query=args.query,
        domain=args.domain,
        seniority=args.seniority,
        is_remote=args.remote,
        is_fresher=args.fresher,
        portal=args.portal,
        limit=5
    )
    
    console.print(f"\n[bold]Search: '{args.query}'[/bold] (source: {result['source']})")
    console.print(f"[dim]Total: {result['total']} jobs[/dim]\n")
    
    if result['hits']:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim")
        table.add_column("Title")
        table.add_column("Company")
        table.add_column("Domain")
        table.add_column("Score", justify="right")
        
        for i, job in enumerate(result['hits'][:5], 1):
            score = job.get('_score', 0) if result['source'] == 'es' else job.get('rank_score', 0)
            table.add_row(
                str(i),
                job.get('title', 'N/A')[:40],
                job.get('company', 'N/A')[:25],
                job.get('domain', 'N/A')[:20],
                f"{score:.2f}"
            )
        console.print(table)
    else:
        console.print("[yellow]No results found[/yellow]")


def main():
    banner()

    parser = argparse.ArgumentParser(description="Job Extractor CLI")
    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run", help="Run pipeline once")
    run_parser.add_argument("--portals", nargs="+", help="Specific portals to scrape")
    run_parser.add_argument("--max", type=int, default=200, help="Max jobs per portal")
    run_parser.add_argument("--db", action="store_true", help="Also save to PostgreSQL")

    # schedule
    sched_parser = subparsers.add_parser("schedule", help="Start cron scheduler")
    sched_parser.add_argument("--hours", type=int, default=6, help="Interval hours")
    sched_parser.add_argument("--db", action="store_true", help="Also save to PostgreSQL")

    # test-scraper
    ts_parser = subparsers.add_parser("test-scraper", help="Test one scraper")
    ts_parser.add_argument("portal", help="Portal name (e.g. remotive)")

    # test-nlp
    subparsers.add_parser("test-nlp", help="Run NLP on a sample job")

    # stats
    subparsers.add_parser("stats", help="Show stats from saved data")

    # db commands
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    
    db_subparsers.add_parser("migrate", help="Run alembic upgrade head")
    
    seed_parser = db_subparsers.add_parser("seed", help="Seed database from processed JSON")
    seed_parser.add_argument("--file", type=str, help="Specific JSON file to seed from")
    
    db_subparsers.add_parser("status", help="Show migration status and job count")

    # es commands
    es_parser = subparsers.add_parser("es", help="Elasticsearch operations")
    es_subparsers = es_parser.add_subparsers(dest="es_command")
    
    es_subparsers.add_parser("index", help="Index all processed JSON into ES")
    es_subparsers.add_parser("status", help="Show ES health and job count")

    # search command
    search_parser = subparsers.add_parser("search", help="Search jobs (test)")
    search_parser.add_argument("query", nargs="?", default="", help="Search query")
    search_parser.add_argument("--domain", type=str, help="Filter by domain")
    search_parser.add_argument("--seniority", type=str, help="Filter by seniority")
    search_parser.add_argument("--remote", action="store_true", help="Remote jobs only")
    search_parser.add_argument("--fresher", action="store_true", help="Fresher-friendly only")
    search_parser.add_argument("--portal", type=str, help="Filter by portal")

    args = parser.parse_args()

    if args.command == "run":
        asyncio.run(cmd_run(args))

    elif args.command == "schedule":
        from scheduler.runner import PipelineScheduler
        sched = PipelineScheduler(interval_hours=args.hours, use_db=args.db)
        sched.start()

    elif args.command == "test-scraper":
        asyncio.run(cmd_test_scraper(args))

    elif args.command == "test-nlp":
        asyncio.run(cmd_test_nlp(args))

    elif args.command == "stats":
        cmd_stats(args)

    elif args.command == "db":
        if args.db_command == "migrate":
            cmd_db_migrate(args)
        elif args.db_command == "seed":
            cmd_db_seed(args)
        elif args.db_command == "status":
            cmd_db_status(args)
        else:
            db_parser.print_help()

    elif args.command == "es":
        if args.es_command == "index":
            cmd_es_index(args)
        elif args.es_command == "status":
            cmd_es_status(args)
        else:
            es_parser.print_help()

    elif args.command == "search":
        cmd_search(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
