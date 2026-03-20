"""
JSON file storage — development fallback when PostgreSQL isn't available.
Also used to persist raw and processed data between pipeline runs.
"""
from __future__ import annotations
import json
import uuid
from datetime import datetime
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.models import RawJob, ProcessedJob
from utils.logger import logger
from config.settings import DATA_RAW, DATA_PROCESSED


class JSONStorage:
    """
    Simple JSON file storage for development / offline use.
    Production uses PostgresStorage instead.
    """

    def __init__(
        self,
        raw_dir: Path = DATA_RAW,
        processed_dir: Path = DATA_PROCESSED,
    ):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def save_raw(self, jobs: list[RawJob], run_id: str = None) -> Path:
        """Save raw jobs from scraper output."""
        run_id = run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = self.raw_dir / f"raw_{run_id}.json"

        data = [job.model_dump(mode="json") for job in jobs]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

        logger.info(f"[JSONStorage] Saved {len(jobs)} raw jobs → {path}")
        return path

    def save_processed(self, jobs: list[ProcessedJob], run_id: str = None) -> Path:
        """Save processed + enriched jobs."""
        run_id = run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = self.processed_dir / f"processed_{run_id}.json"

        data = [job.model_dump(mode="json") for job in jobs]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

        logger.info(f"[JSONStorage] Saved {len(jobs)} processed jobs → {path}")
        return path

    def load_raw(self, path: Path | str) -> list[RawJob]:
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [RawJob(**item) for item in data]

    def load_processed(self, path: Path | str = None) -> list[ProcessedJob]:
        """Load the most recent processed file if path not given."""
        if path is None:
            files = sorted(self.processed_dir.glob("processed_*.json"), reverse=True)
            if not files:
                logger.warning("[JSONStorage] No processed files found.")
                return []
            path = files[0]
            logger.info(f"[JSONStorage] Loading latest: {path.name}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [ProcessedJob(**item) for item in data]

    def load_all_processed(self) -> list[ProcessedJob]:
        """Load and merge all processed files (for dashboard data)."""
        all_jobs: list[ProcessedJob] = []
        seen_fingerprints: set[str] = set()

        for path in sorted(self.processed_dir.glob("processed_*.json"), reverse=True):
            jobs = self.load_processed(path)
            for job in jobs:
                if job.fingerprint not in seen_fingerprints:
                    seen_fingerprints.add(job.fingerprint)
                    all_jobs.append(job)

        logger.info(f"[JSONStorage] Loaded {len(all_jobs)} unique jobs from all files")
        return all_jobs

    def get_stats(self, jobs: list[ProcessedJob] = None) -> dict:
        """Generate quick stats for the CLI summary."""
        if jobs is None:
            jobs = self.load_all_processed()

        if not jobs:
            return {"total": 0}

        from collections import Counter

        domains = Counter(j.domain for j in jobs)
        portals = Counter(j.source_portal for j in jobs)
        skills_flat = []
        for j in jobs:
            skills_flat.extend(j.skills)
        top_skills = Counter(skills_flat).most_common(15)

        return {
            "total": len(jobs),
            "fresher_friendly": sum(1 for j in jobs if j.is_fresher_friendly),
            "remote": sum(1 for j in jobs if j.is_remote),
            "domain_distribution": dict(domains.most_common()),
            "portal_distribution": dict(portals.most_common()),
            "top_skills": dict(top_skills),
        }
