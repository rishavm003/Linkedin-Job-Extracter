# 🚀 JobExtractor: Production-Grade Job Ingestion Platform

A high-performance, modular monorepo for scraping, analyzing, and searching job listings—specifically optimized for Indian freshers and entry-level developers.

## 🏗️ Architecture
- **Apps**:
  - `web`: Next.js 16 (Dashboard & Analytics)
  - `api`: FastAPI (Backend & AI Search)
  - `worker`: Python (Scrapers & NLP Pipeline)
- **Libs**:
  - `core`: Shared models, logging, and configuration
  - `database`: PostgreSQL, Redis, and Elasticsearch storage layer

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
