import argparse
import asyncio
import sys
import os
from rich.console import Console
from rich.table import Table

# Add root directory to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'apps', 'worker'))

from libs.core.logger import logger

console = Console()

def banner():
    console.print(r"""
    [bold cyan]
     _  _  ____  ____  ____  _  _  ____  ____   __    ___  ____  _____  ____ 
    ( )( )(  _ \(  _ \(  __)( \/ )(_  _)(  _ \ / _\  / __)(_  _)(  _  )(  _ \\
     )__(  )   / )   / ) _)  )  (   )(   )   //    \( (__   )(   )(_)(  )   /
    (__)(__)(__\_)(__\_)(____)(_/\_) (__) (__\_)\_/\_/ \___) (__) (_____)(__\_)
    [/bold cyan]
    [bold yellow]--- Automated Multi-Portal Job Extraction Platform ---[/bold yellow]
    """)

async def cmd_run(args):
    """Run the pipeline once."""
    from scheduler.runner import run_pipeline
    await run_pipeline(
        portals=args.portals,
        max_per_portal=args.max,
        use_db=args.db
    )

async def cmd_test_scraper(args):
    """Test a single scraper."""
    from scrapers.orchestrator import ScraperOrchestrator
    orchestrator = ScraperOrchestrator(portals=[args.portal])
    await orchestrator.run()

async def cmd_test_nlp(args):
    """Test NLP extraction."""
    from nlp.pipeline import NLPPipeline
    from libs.core.models import RawJob
    
    sample_text = """
    Python Developer at TechCorp.
    Requirements: 3+ years experience with Django, PostgreSQL, and AWS.
    Location: Bangalore. Salary: 15-25 LPA.
    """
    job = RawJob(
        title="Python Developer",
        company="TechCorp",
        location="Bangalore",
        description=sample_text,
        portal="manual_test"
    )
    
    nlp = NLPPipeline()
    processed = nlp.run([job])
    console.print(processed[0].model_dump_json(indent=2))

def cmd_stats(args):
    """Show overall statistics."""
    from apps.worker.storage.json_storage import JSONStorage
    store = JSONStorage()
    files = os.listdir(store.processed_dir)
    console.print(f"[cyan]Total runs:[/cyan] {len(files)}")
    # More detailed stats could be added here

def cmd_db_migrate(args):
    """Run database migrations."""
    import subprocess
    cmd = ["alembic", "upgrade", "head"]
    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
    subprocess.run(cmd)

def cmd_db_seed(args):
    """Seed database from JSON files."""
    import json
    import glob
    from libs.database.postgres import PostgresStorage
    from libs.core.models import ProcessedJob
    
    pg = PostgresStorage()
    pg.create_tables()
    
    files = glob.glob("data/processed/*.json")
    if args.file:
        files = [args.file]
        
    for f in files:
        console.print(f"[dim]Seeding from {f}...[/dim]")
        with open(f, 'r') as file:
            data = json.load(file)
            jobs = [ProcessedJob(**j) for j in data]
            pg.save_jobs(jobs)

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

    # db
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    db_subparsers.add_parser("migrate", help="Run alembic migrations")
    db_seed = db_subparsers.add_parser("seed", help="Seed from JSON")
    db_seed.add_argument("--file", help="Specific file")

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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
