"""Check database contents."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dependencies import get_postgres

def check_db():
    """Check database contents."""
    pg = get_postgres()
    
    # Get job count
    count = pg.get_job_count()
    print(f"Total jobs in DB: {count}")
    
    # Get some jobs
    jobs = pg.get_jobs(limit=5)
    if jobs:
        print(f"First job: {jobs[0]['title']}")
        print(f"Job keys: {list(jobs[0].keys())}")
    else:
        print("No jobs found!")

if __name__ == "__main__":
    check_db()
