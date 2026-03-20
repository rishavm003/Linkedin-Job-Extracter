"""
Central configuration for the Job Extractor pipeline.
All secrets come from .env — never hardcode credentials.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Project paths ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
LOGS_DIR = BASE_DIR / "logs"

for _dir in (DATA_RAW, DATA_PROCESSED, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/jobextractor"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_INDEX = "jobs"

# ── Scraper behaviour ─────────────────────────────────────────────────────────
SCRAPER_DELAY_MIN = 2.0       # seconds between requests (be polite)
SCRAPER_DELAY_MAX = 5.0
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30          # seconds
MAX_JOBS_PER_PORTAL = 500     # safety cap per run
PLAYWRIGHT_HEADLESS = True
PLAYWRIGHT_SLOW_MO = 500      # ms — reduces bot detection

# ── Scheduler ─────────────────────────────────────────────────────────────────
SCRAPE_INTERVAL_HOURS = 6     # how often to re-scrape

# ── NLP ───────────────────────────────────────────────────────────────────────
SPACY_MODEL = "en_core_web_sm"
SIMILARITY_THRESHOLD = 0.85   # for deduplication

# ── Portal targets (freshers / entry-level focused) ───────────────────────────
PORTALS = {
    "remotive": {
        "enabled": True,
        "base_url": "https://remotive.com/api/remote-jobs",
        "type": "api",           # has a free JSON API — best starting point
    },
    "remoteok": {
        "enabled": True,
        "base_url": "https://remoteok.com/api",
        "type": "api",
    },
    "github_jobs_archive": {
        "enabled": True,
        "base_url": "https://www.arbeitnow.com/api/job-board-api",
        "type": "api",           # arbeitnow has a free API, great for EU + remote
    },
    "internshala": {
        "enabled": True,
        "base_url": "https://internshala.com/internships",
        "type": "scraper",
    },
    "naukri": {
        "enabled": True,
        "base_url": "https://www.naukri.com/jobs-in-india",
        "type": "scraper",
    },
    "indeed": {
        "enabled": True,
        "base_url": "https://www.indeed.com/jobs",
        "type": "scraper",
    },
    "linkedin": {
        "enabled": True,
        "base_url": "https://www.linkedin.com/jobs/search",
        "type": "scraper",
    },
    "wellfound": {
        "enabled": True,
        "base_url": "https://wellfound.com/jobs",   # AngelList successor, startup jobs
        "type": "scraper",
    },
    "freshersnow": {
        "enabled": True,
        "base_url": "https://freshersnow.com/category/freshers-jobs/",
        "type": "scraper",
    },
}

# ── Search keywords for fresher jobs ─────────────────────────────────────────
FRESHER_KEYWORDS = [
    "fresher", "entry level", "0-1 years", "0-2 years",
    "junior", "trainee", "intern", "graduate", "campus hire",
    "recent graduate", "new grad",
]

JOB_DOMAINS = [
    "Software Development",
    "Data Science & ML",
    "DevOps & Cloud",
    "Frontend Development",
    "Backend Development",
    "Full Stack Development",
    "Mobile Development",
    "Cybersecurity",
    "UI/UX Design",
    "Product Management",
    "Data Analysis",
    "Digital Marketing",
    "Content Writing",
    "Finance & Accounting",
    "HR & Recruitment",
    "Customer Support",
    "Sales",
    "Operations",
    "Research",
    "Other",
]
