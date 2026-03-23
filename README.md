# JobExtractor — Multi-Portal Job Intelligence Platform

Automatically scrapes 13+ job portals, extracts skills and domains using NLP, and serves a beautiful dashboard for Indian freshers and students.

## 🚀 Quick Start (One Command)

```bash
git clone https://github.com/rishavm003/Linkedin-Job-Extracter
cd Linkedin-Job-Extracter
cp .env.example .env
# Edit .env with your API keys
bash scripts/deploy.sh
```

## 🌟 What You Get

- **Dashboard**: http://localhost (job board + analytics)
- **API docs**: http://localhost/docs (interactive Swagger UI)
- **API health**: http://localhost/api/health
- **AI Assistant**: http://localhost/ai (with Ollama)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Frontend   │  │   Backend   │  │   Pipeline  │  │
│  │ (Next.js)   │  │  (FastAPI)  │ │(Scrapers+NLP)│  │
│  │    :3000    │  │    :8000    │  │             │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│         │                │                │              │
│         └────────────────┼────────────────┘              │
│                          │                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Data Layer                          │  │
│  │  ┌─────────────┐  ┌─────────────┐           │  │
│  │  │ PostgreSQL  │  │Elasticsearch│  │  │
│  │  │   :5432     │  │   :9200     │  │  │
│  │  └─────────────┘  └─────────────┘           │  │
│  │  ┌─────────────┐  ┌─────────────┐           │  │
│  │  │    Redis    │  │   Ollama    │  │  │
│  │  │   :6379     │  │   :11434    │  │  │
│  │  └─────────────┘  └─────────────┘           │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| **Backend** | FastAPI, SQLAlchemy, Alembic, Pydantic |
| **Database** | PostgreSQL, Redis, Elasticsearch |
| **AI** | Ollama, LangChain, llama3.1:8b |
| **Scraping** | Playwright, HTTPX, BeautifulSoup4 |
| **NLP** | spaCy, scikit-learn, NLTK |
| **Infrastructure** | Docker, Nginx, GitHub Actions |
| **Deployment** | Render, Railway, Vercel, AWS ECS |

## 📊 Portals Covered

| Portal | Type | Auth | Jobs | Region |
|--------|------|-------|-------|--------|
| Remotive | API | ✗ | Remote | Global |
| RemoteOK | API | ✗ | Remote | Global |
| Arbeitnow | API | ✗ | All | Global |
| Adzuna | API | ✅ | All | Global |
| RapidAPI | API | ✅ | All | Global |
| Internshala | Scraper | ✗ | Internships | India |
| Naukri | Scraper | ✗ | Jobs | India |
| LinkedIn | Scraper | ✗ | Jobs | Global |
| FreshersNow | Scraper | ✗ | Freshers | India |
| FindWork | API | ✅ | Remote | Global |
| Jooble | API | ✅ | All | Global |
| The Muse | API | ✅ | All | Global |
| Reed | API | ✅ | Jobs | UK |

## 🔑 API Keys Required

| API | Where to Register | Free Tier |
|-----|------------------|------------|
| **Adzuna** | https://developer.adzuna.com | 1,000 requests/day |
| **RapidAPI** | https://rapidapi.com/hub | 500 requests/month |
| **Apyhub** | https://apyhub.com | 1,000 requests/month |
| **FindWork** | https://findwork.dev | 100 requests/month |
| **Jooble** | https://jooble.org/api | 1,000 requests/day |
| **The Muse** | https://www.themuse.com/developers | 1,000 requests/month |
| **Reed** | https://www.reed.co.uk/developers | 1,000 requests/month |



## 🤖 With AI Assistant

```bash
# Start with AI features
docker compose --profile ai up -d
bash scripts/setup_ollama.sh
```

## 📋 Common Commands

```bash
# Deployment
bash scripts/deploy.sh    # Full production deploy
bash scripts/stop.sh      # Stop all services

# Manual Operations
python main.py run        # Manual scrape run
python main.py stats      # Show job statistics
pytest tests/ -v          # Run all tests

# Docker Operations
docker compose ps          # Check service status
docker compose logs -f     # View logs
docker compose down -v     # Stop + remove data
```

## 📁 Project Structure

```
jobextractor/
├── 📂 jobextractor/          # Phase 1: Scrapers + NLP
│   ├── scrapers/             # 13 portal scrapers
│   ├── nlp/                  # Text processing pipeline
│   ├── storage/              # Database adapters
│   ├── scheduler/            # Cron jobs
│   ├── config/               # Settings & skills taxonomy
│   ├── utils/                # Models & utilities
│   ├── scripts/              # Setup scripts
│   └── main.py              # CLI entry point
├── 📂 backend/               # Phase 3: FastAPI
│   ├── routers/              # API endpoints
│   ├── services/             # Business logic
│   ├── schemas/              # Pydantic models
│   └── tests/                # Backend tests
├── 📂 frontend/              # Phase 4: Next.js
│   ├── src/app/              # App router pages
│   ├── src/components/       # UI components
│   ├── src/hooks/            # React hooks
│   └── src/lib/              # Utilities & API client
├── 📂 nginx/                 # Reverse proxy config
├── 📂 scripts/               # Deployment scripts
├── 📂 .github/workflows/      # CI/CD
├── 🐳 docker-compose.yml      # Production stack
├── 🐳 docker-compose.dev.yml # Development stack
└── 📚 README.md              # This file
```

## 🧪 Testing

```bash
# All tests
pytest tests/ -v

# Pipeline tests only
cd jobextractor && pytest tests/ -v

# Backend tests only
cd backend && pytest tests/ -v

# Frontend build
cd frontend && npm run build && npm run test
```

## 📈 Monitoring & Analytics

- **Real-time job scraping** (every 6 hours)
- **Skill demand tracking** across domains
- **Salary analytics** by experience level
- **Portal performance** metrics
- **AI-powered job matching**

## 🔒 Security Features

- **Rate limiting** (30 req/min API, 10 req/min AI)
- **CORS protection** with proper origins
- **Security headers** (XSS, CSRF protection)
- **Environment variables** (no hardcoded secrets)
- **Health checks** on all services

## 🚀 Production Deployment

### Render (Recommended)
```bash
# Deploy to Render
git push origin main
# Render auto-deploys from render.yaml
```

### Railway
```bash
# Deploy to Railway
railway login
railway up
```

### Vercel (Frontend only)
```bash
# Deploy frontend to Vercel
cd frontend
vercel --prod
```

## 🎯 Key Features

### 🎓 Fresher-Focused
- Specialized filtering for entry-level positions
- Internship tracking and alerts
- Salary expectations for 0-2 years experience
- Skill gap analysis for freshers

### 🤖 Intelligent Matching
- AI-powered job recommendations
- Natural language job search
- Contextual question answering
- Skill-based matching algorithm

### 📊 Real-Time Analytics
- Live job market insights
- Trending skills analysis
- Salary benchmarks by location
- Portal performance comparison

### 🔄 Automated Pipeline
- Continuous job scraping
- Deduplication across portals
- NLP-powered enrichment
- Automatic database updates

## 🌍 Deployment Options

| Platform | Type | Cost | Setup Time |
|----------|------|-------|------------|
| **Render** | Full Stack | Free tier | 5 min |
| **Railway** | Full Stack | $5/month | 5 min |
| **DigitalOcean** | Full Stack | $200 credit | 10 min |
| **AWS ECS** | Full Stack | Pay-as-you-go | 30 min |
| **Vercel** | Frontend Only | Free tier | 2 min |

## 📞 Support & Contributing

1. **Issues**: Report bugs via GitHub Issues
2. **Contributions**: Fork → Branch → PR → Merge
3. **Documentation**: Update README and inline comments
4. **Tests**: Ensure all tests pass before PR

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🎉 All Phases Complete!

**JobExtractor is now a production-ready job intelligence platform with:**

✅ **13+ Job Portals** scraped automatically  
✅ **AI Assistant** with local LLM  
✅ **Real-time Analytics** and dashboards  
✅ **Docker Deployment** for any cloud  
✅ **CI/CD Pipeline** with GitHub Actions  
✅ **Production Monitoring** and health checks  

**Start your job search platform in under 10 minutes!**

```bash
git clone https://github.com/rishavm003/Linkedin-Job-Extracter
cd Linkedin-Job-Extracter
cp .env.example .env
# Add your API keys to .env
bash scripts/deploy.sh
```

**🚀 Happy job hunting!**

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
