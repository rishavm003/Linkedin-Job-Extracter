import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1. Find root directory
# This file is in libs/core/config.py, so parent.parent.parent is root.
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

# 2. Project paths
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"

for _dir in (DATA_DIR, LOGS_DIR, DATA_RAW, DATA_PROCESSED):
    _dir.mkdir(parents=True, exist_ok=True)

# 3. Database & Cache
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/jobextractor"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_INDEX = "jobs"

# 4. Scraper behaviour
SCRAPER_DELAY_MIN = 2.0
SCRAPER_DELAY_MAX = 5.0
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
MAX_JOBS_PER_PORTAL = int(os.getenv("MAX_JOBS_PER_PORTAL", "100"))
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "True").lower() == "true"
PLAYWRIGHT_SLOW_MO = 1000
MEMORY_SAVER_MODE = os.getenv("MEMORY_SAVER_MODE", "True").lower() == "true"
NLP_MAX_WORKERS = int(os.getenv("NLP_MAX_WORKERS", "2"))

# 5. Scheduler
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))

# 6. NLP
SPACY_MODEL = "en_core_web_sm"
SIMILARITY_THRESHOLD = 0.85

# 7. External API Keys
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
APYHUB_API_KEY = os.getenv("APYHUB_API_KEY", "")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
ARBEITNOW_API_URL = os.getenv("ARBEITNOW_API_URL", "https://www.arbeitnow.com/api/job-board-api")

# 8. Load constants (must be imported AFTER paths are set)
try:
    from libs.core.constants import FRESHER_KEYWORDS, PORTALS, JOB_DOMAINS
except ImportError:
    # Fallback for when libs.core is not yet in path
    FRESHER_KEYWORDS = ["fresher", "junior", "intern", "entry level"]
    PORTALS = {}
    JOB_DOMAINS = []
