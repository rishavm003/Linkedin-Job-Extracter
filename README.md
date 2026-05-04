# 🚀 JobExtractor: Production-Grade Job Ingestion Platform

A high-performance, modular monorepo for scraping, analyzing, and searching job listings—specifically optimized for Indian freshers and entry-level developers.

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

## ⚡ Quick Start

### 1. Prerequisites
- **Node.js 18+** & **Python 3.11+ (64-bit recommended)**
- **Docker Desktop** (for Postgres, ES, and Redis)
- **Ollama** (optional, for AI features)

### 2. Setup
1. **Clone the project**
2. **Setup Environment**:
   ```bash
   copy .env.example .env
   ```
3. **Install Dependencies**:
   ```bash
   # Install Python requirements
   pip install -r requirements.txt
   
   # Install Node dependencies
   npm install
   ```

### 3. Launch (Windows)
Simply run the production launch system:
```bash
./run.bat
```
*This will automatically start the databases, verify dependencies, and launch the Web app, API, and Scraper Scheduler.*

---

## 🔗 Service Map
| Service | URL | Description |
| :--- | :--- | :--- |
| **Dashboard** | [http://localhost:3001](http://localhost:3001) | Main UI & Analytics |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | OpenAPI / Swagger UI |
| **AI Query** | `POST /api/ai/query` | Natural language job search |

---

## 🛠️ Developer Commands
- **Run Scraper Once**: `npm run worker`
- **Database Only**: `npm run db` (starts Docker containers)
- **Playwright Setup**: `playwright install chromium`

---

## 📦 Sending this project to others
To share this project, simply zip the entire folder **EXCEPT** for these (which are ignored by `.gitignore`):
- `venv/`
- `node_modules/`
- `data/` & `logs/`
- `.next/`

The recipient just needs to follow the **Setup** steps above.
