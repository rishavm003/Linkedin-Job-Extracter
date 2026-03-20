import sys
import os
import json
import glob
import argparse
import subprocess
from datetime import datetime
from rich.console import Console
from rich.table import Table

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.postgres import PostgresStorage
from utils.models import ProcessedJob
from utils.logger import logger

console = Console()

def parse_datetime(val):
    if not val:
        return None
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace('Z', '+00:00'))
        except ValueError:
            return None
    return val

def run_migrations():
    """Run alembic upgrade head to ensure schema is ready."""
    console.print("[dim]Running database migrations...[/dim]")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True, text=True)
        console.print("[green]✓ Schema is up to date[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Migration failed:[/red]\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        console.print("[red]alembic command not found. Ensure it is installed.[/red]")
        sys.exit(1)

def seed_database(specific_file=None):
    """Seed the database from processed JSON files."""
    run_migrations()
    
    if specific_file:
        files = [specific_file]
    else:
        files = glob.glob(os.path.join("data", "processed", "processed_*.json"))
        
    if not files:
        console.print("[yellow]No processed files found to seed![/yellow]")
        return
        
    all_jobs = []
    skipped_files = 0
    
    console.print(f"[dim]Loading {len(files)} file(s)...[/dim]")
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                # Handle datetime strings
                for d_field in ["posted_at", "scraped_at", "processed_at"]:
                    if d_field in item and item[d_field]:
                        item[d_field] = parse_datetime(item[d_field])
                
                all_jobs.append(ProcessedJob(**item))
        except Exception as e:
            logger.warning(f"Failed to read/parse {filepath}: {e}")
            skipped_files += 1

    total_records = len(all_jobs)
    if total_records == 0:
        console.print("[yellow]No valid job records found in files.[/yellow]")
        return
        
    console.print(f"[cyan]Found {total_records} records. Saving to PostgreSQL...[/cyan]")
    
    pg = PostgresStorage()
    inserted, skipped = pg.save_jobs(all_jobs)
    
    # Print summary table
    table = Table(title="Database Seed Summary", border_style="cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    
    table.add_row("Files loaded", str(len(files) - skipped_files))
    if skipped_files > 0:
        table.add_row("Files skipped/errors", f"[red]{skipped_files}[/red]")
    table.add_row("Total records read", str(total_records))
    table.add_row("Inserted (New)", f"[green]{inserted}[/green]")
    table.add_row("Skipped (Duplicates)", f"[yellow]{skipped}[/yellow]")
    
    console.print("\n")
    console.print(table)
    console.print("\n[bold green]Seed process complete![/bold green]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed PostgreSQL database with processed JSON data")
    parser.add_argument("--file", type=str, help="Specific JSON file to seed from")
    args = parser.parse_args()
    
    seed_database(args.file)
