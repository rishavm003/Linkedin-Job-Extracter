# Job Extractor — Phase 1: Scraper + NLP Pipeline

> Multi-portal job scraper with NLP-powered extraction, built for freshers & students.

---

## Project Structure

```
jobextractor/
├── main.py                    ← CLI entry point (run this!)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example               ← copy to .env
│
├── config/
│   ├── settings.py            ← all config & constants
│   └── skills_taxonomy.py     ← 200+ skills across 8 domains
│
├── scrapers/
│   ├── base.py                ← BaseScraper (HTTP + Playwright)
│   ├── orchestrator.py        ← runs all scrapers, merges results
│   ├── remotive_scraper.py    ← FREE API ✓
│   ├── remoteok_scraper.py    ← FREE API ✓
│   ├── arbeitnow_scraper.py   ← FREE API ✓
│   ├── internshala_scraper.py ← Playwright (India internships)
│   ├── naukri_scraper.py      ← Playwright (India jobs)
│   ├── linkedin_scraper.py    ← Playwright (public search)
│   └── freshersnow_scraper.py ← HTTP (India freshers)
│
├── nlp/
│   ├── text_cleaner.py        ← HTML strip, normalise, salary regex
│   ├── extractor.py           ← skills, domain, seniority, salary
│   ├── deduplicator.py        ← fingerprint + fuzzy + embedding dedup
│   └── pipeline.py            ← orchestrates NLP, supports multiprocessing
│
├── storage/
│   ├── postgres.py            ← PostgreSQL via SQLAlchemy (production)
│   └── json_storage.py        ← JSON file storage (dev / offline)
│
├── scheduler/
│   └── runner.py              ← APScheduler cron + CLI summary
│
├── utils/
│   ├── models.py              ← Pydantic models (RawJob, ProcessedJob)
│   └── logger.py              ← Loguru setup
│
├── tests/
│   └── test_pipeline.py       ← pytest test suite
│
└── data/
    ├── raw/                   ← raw scraper output (JSON per run)
    └── processed/             ← NLP-enriched output (JSON per run)
```

---

## Quick Start

### 1. Install dependencies

```bash
cd jobextractor
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
playwright install chromium
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your database URL (or leave defaults for local dev)
```

### 3. Run the pipeline

```bash
# Run once (saves to data/processed/)
python main.py run

# Run specific portals only
python main.py run --portals remotive remoteok arbeitnow

# Run with max 50 jobs per portal
python main.py run --max 50

# Start scheduler (every 6 hours)
python main.py schedule --hours 6
```

### 4. Using Docker (recommended for full stack)

```bash
docker compose up -d
# Pipeline starts automatically on cron every 6 hours
# PostgreSQL available at localhost:5432
```

---

## CLI Commands

| Command | Description |
|---|---|
| `python main.py run` | Run full pipeline once |
| `python main.py run --portals remotive remoteok` | Only specific portals |
| `python main.py run --max 100 --db` | 100 jobs/portal + save to PostgreSQL |
| `python main.py schedule --hours 6` | Start cron scheduler |
| `python main.py test-scraper remotive` | Test one scraper live |
| `python main.py test-nlp` | Test NLP on a sample job |
| `python main.py stats` | Show stats from saved data |

---

## Portal Overview

| Portal | Type | Freshers? | Auth needed? |
|---|---|---|---|
| Remotive | Free API | ✓ | ✗ |
| RemoteOK | Free API | ✓ | ✗ |
| Arbeitnow | Free API | ✓ | ✗ |
| Internshala | Playwright | ✓✓ India | ✗ |
| FreshersNow | HTTP | ✓✓ India | ✗ |
| Naukri | Playwright | ✓ India | ✗ |
| LinkedIn | Playwright | ✓ | ✗ (public search) |

---

## What the NLP Pipeline Extracts

From every job description, the pipeline extracts:

- **Skills** — matched against a 200+ skill taxonomy (Python, React, SQL, etc.)
- **Domain** — Software Dev, Data Science, DevOps, Frontend, Mobile, etc.
- **Seniority** — Fresher / Intern / Entry Level / Mid / Senior
- **Salary** — parsed from raw text, supports INR (LPA) and USD formats
- **Qualifications** — B.Tech, BCA, MCA, etc.
- **Experience required** — "0-1 years", "1-2 years", etc.
- **Fresher-friendly flag** — boolean, used for filtering in dashboard
- **Remote flag** — detected from location + description keywords
- **Location** — normalised (Bengaluru → Bangalore, etc.)
- **Summary** — first 350 chars of cleaned description

---

## Running Tests

```bash
pytest tests/test_pipeline.py -v

# Include live API tests (hits real portals)
LIVE_TEST=1 pytest tests/test_pipeline.py -v -k "live"
```

---

## Next Phases

- **Phase 2** — Database schema migrations (Alembic) + Elasticsearch indexing
- **Phase 3** — FastAPI backend with REST API + filters
- **Phase 4** — Next.js dashboard with job board + analytics charts
- **Phase 5** — AI query interface (LangChain + Ollama / Llama 3)
- **Phase 6** — Docker full-stack deployment + Vercel/Render deploy
