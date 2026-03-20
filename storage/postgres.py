"""
Storage layer — PostgreSQL via SQLAlchemy.
Handles saving ProcessedJobs, checking for duplicates, and querying.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import (
    create_engine, Column, String, Boolean, Float,
    DateTime, Text, JSON, Integer, Index, text
)
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import plainto_tsquery

from config.settings import DATABASE_URL
from utils.models import ProcessedJob
from utils.logger import logger

Base = declarative_base()


class JobRecord(Base):
    """
    SQLAlchemy ORM model — maps directly to the `jobs` table.
    """
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)

    # Core fields
    title = Column(String(300), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    is_remote = Column(Boolean, default=False)
    country = Column(String(100))
    city = Column(String(100))

    # Portal info
    source_portal = Column(String(50), nullable=False, index=True)
    portal_display_name = Column(String(100))
    apply_url = Column(Text, nullable=False)

    # Categorisation
    job_type = Column(String(50), default="Full-time")
    seniority = Column(String(50), default="Entry Level", index=True)
    domain = Column(String(100), index=True)

    # NLP-extracted (stored as JSON arrays)
    skills = Column(JSON, default=list)
    qualifications = Column(JSON, default=list)
    soft_skills = Column(JSON, default=list)

    # Salary
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True)
    salary_period = Column(String(20), nullable=True)
    salary_disclosed = Column(Boolean, default=False)
    salary_raw = Column(String(200), nullable=True)

    # Dates
    posted_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, default=datetime.utcnow)

    # Description
    description_clean = Column(Text)
    description_summary = Column(Text)

    # Fresher flags
    is_fresher_friendly = Column(Boolean, default=False, index=True)
    requires_experience = Column(String(100), nullable=True)

    # Soft-delete + active flag
    is_active = Column(Boolean, default=True, index=True)

    __table_args__ = (
        Index("ix_jobs_domain_seniority", "domain", "seniority"),
        Index("ix_jobs_portal_active", "source_portal", "is_active"),
        Index("ix_jobs_fresher_remote", "is_fresher_friendly", "is_remote"),
    )

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PostgresStorage:
    """
    Handles all interactions with the PostgreSQL database.
    """

    def __init__(self, database_url: str = DATABASE_URL):
        """Initialize PostgreSQL storage with graceful fallback."""
        # Detect if using SQLite for testing
        is_sqlite = database_url.startswith("sqlite")
        
        if is_sqlite:
            # SQLite doesn't support pool_size, max_overflow, etc.
            self.engine = create_engine(database_url)
        else:
            self.engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
            )
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        logger.info(f"[Storage] Database connected ({'SQLite' if is_sqlite else 'PostgreSQL'})")

    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("[Storage] Tables created / verified")

    def get_session(self) -> Session:
        return self.SessionLocal()

    def save_jobs(self, jobs: list[ProcessedJob]) -> tuple[int, int]:
        """
        Upsert a list of ProcessedJobs.
        Returns (inserted_count, skipped_count).
        """
        if not jobs:
            return 0, 0

        inserted = 0
        skipped = 0

        with self.get_session() as session:
            for job in jobs:
                try:
                    record = self._to_record(job)
                    # Upsert: insert or skip if fingerprint already exists
                    stmt = pg_insert(JobRecord).values(**record)
                    stmt = stmt.on_conflict_do_nothing(index_elements=["fingerprint"])
                    result = session.execute(stmt)
                    if result.rowcount > 0:
                        inserted += 1
                    else:
                        skipped += 1
                except Exception as e:
                    logger.warning(f"[Storage] Failed to save '{job.title}': {e}")
                    session.rollback()
                    skipped += 1
            session.commit()

        logger.info(f"[Storage] Saved: {inserted} new, {skipped} duplicates skipped")
        return inserted, skipped

    def get_jobs(
        self,
        domain: Optional[str] = None,
        seniority: Optional[str] = None,
        is_remote: Optional[bool] = None,
        portal: Optional[str] = None,
        is_fresher: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Flexible query with filters."""
        with self.get_session() as session:
            q = session.query(JobRecord).filter(JobRecord.is_active == True)

            if domain:
                q = q.filter(JobRecord.domain == domain)
            if seniority:
                q = q.filter(JobRecord.seniority == seniority)
            if is_remote is not None:
                q = q.filter(JobRecord.is_remote == is_remote)
            if portal:
                q = q.filter(JobRecord.source_portal == portal)
            if is_fresher is not None:
                q = q.filter(JobRecord.is_fresher_friendly == is_fresher)

            q = q.order_by(JobRecord.scraped_at.desc())
            results = q.offset(offset).limit(limit).all()
            return [r.to_dict() for r in results]

    def get_stats(self) -> dict:
        """Aggregate stats for the dashboard."""
        with self.get_session() as session:
            total = session.query(JobRecord).filter(JobRecord.is_active == True).count()
            fresher = session.query(JobRecord).filter(
                JobRecord.is_fresher_friendly == True,
                JobRecord.is_active == True
            ).count()
            remote = session.query(JobRecord).filter(
                JobRecord.is_remote == True,
                JobRecord.is_active == True
            ).count()

            # Domain distribution
            domain_counts = session.execute(text("""
                SELECT domain, COUNT(*) as cnt
                FROM jobs WHERE is_active = true
                GROUP BY domain ORDER BY cnt DESC
            """)).fetchall()

            # Top skills
            # This requires unnesting the JSON array — works in PostgreSQL
            top_skills = session.execute(text("""
                SELECT skill, COUNT(*) as cnt
                FROM jobs, jsonb_array_elements_text(skills::jsonb) AS skill
                WHERE is_active = true
                GROUP BY skill ORDER BY cnt DESC LIMIT 20
            """)).fetchall()

            # Portal distribution
            portal_counts = session.execute(text("""
                SELECT source_portal, COUNT(*) as cnt
                FROM jobs WHERE is_active = true
                GROUP BY source_portal ORDER BY cnt DESC
            """)).fetchall()

            return {
                "total_jobs": total,
                "fresher_friendly": fresher,
                "remote_jobs": remote,
                "domain_distribution": [
                    {"domain": r[0], "count": r[1]} for r in domain_counts
                ],
                "portal_distribution": [
                    {"portal": r[0], "display_name": r[0], "count": r[1]} for r in portal_counts
                ],
                "top_skills": [
                    {"skill": r[0], "count": r[1]} for r in top_skills
                ],
            }

    def _has_search_vector(self, session: Session) -> bool:
        """Check if search_vector column exists gracefully."""
        try:
            # We can use a simple quick check
            # if we get an error, column doesn't exist
            session.execute(text("SELECT search_vector FROM jobs LIMIT 1"))
            return True
        except Exception:
            session.rollback()
            return False

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        seniority: Optional[str] = None,
        is_remote: Optional[bool] = None,
        is_fresher: Optional[bool] = None,
        portal: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """Perform full-text search using Postgres TSVector or falback ILIKE."""
        with self.get_session() as session:
            has_vector = self._has_search_vector(session)
            
            q = session.query(JobRecord)
            
            if has_vector and query and query.strip():
                # Full-text search using TSVector
                tsquery = sa.func.plainto_tsquery('english', query)
                q = q.filter(JobRecord.search_vector.op('@@')(tsquery))
                
                # We need to add rank_score to the query output
                # Let's use session.query(JobRecord, rank)
                rank = sa.func.ts_rank_cd(sa.column('search_vector'), tsquery).label('rank_score')
                q = session.query(JobRecord, rank)
                q = q.filter(JobRecord.is_active == True)
                q = q.filter(sa.column('search_vector').op('@@')(tsquery))
            else:
                # ILIKE Fallback
                q = session.query(JobRecord, sa.literal(1.0, type_=sa.Float).label('rank_score'))
                q = q.filter(JobRecord.is_active == True)
                if query and query.strip():
                    search_term = f"%{query}%"
                    q = q.filter(sa.or_(
                        JobRecord.title.ilike(search_term),
                        JobRecord.company.ilike(search_term)
                    ))
            
            # Additional Filters
            if domain:
                q = q.filter(JobRecord.domain == domain)
            if seniority:
                q = q.filter(JobRecord.seniority == seniority)
            if is_remote is not None:
                q = q.filter(JobRecord.is_remote == is_remote)
            if portal:
                q = q.filter(JobRecord.source_portal == portal)
            if is_fresher is not None:
                q = q.filter(JobRecord.is_fresher_friendly == is_fresher)
            
            if has_vector and query and query.strip():
                q = q.order_by(sa.desc('rank_score'), JobRecord.scraped_at.desc())
            else:
                q = q.order_by(JobRecord.scraped_at.desc())
            
            results = q.offset(offset).limit(limit).all()
            
            # Format results
            out = []
            for item in results:
                # Results will be (JobRecord, float) tuples
                record, score = item
                dic = record.to_dict()
                dic['rank_score'] = float(score) if score is not None else 0.0
                out.append(dic)
            return out

    def count_search(
        self,
        query: str,
        domain: Optional[str] = None,
        seniority: Optional[str] = None,
        is_remote: Optional[bool] = None,
        is_fresher: Optional[bool] = None,
        portal: Optional[str] = None,
    ) -> int:
        """Count results for pagination based on the same search criteria."""
        with self.get_session() as session:
            has_vector = self._has_search_vector(session)
            
            q = session.query(JobRecord).filter(JobRecord.is_active == True)
            
            if has_vector and query and query.strip():
                tsquery = sa.func.plainto_tsquery('english', query)
                q = q.filter(sa.column('search_vector').op('@@')(tsquery))
            elif query and query.strip():
                search_term = f"%{query}%"
                q = q.filter(sa.or_(
                    JobRecord.title.ilike(search_term),
                    JobRecord.company.ilike(search_term)
                ))
                
            if domain:
                q = q.filter(JobRecord.domain == domain)
            if seniority:
                q = q.filter(JobRecord.seniority == seniority)
            if is_remote is not None:
                q = q.filter(JobRecord.is_remote == is_remote)
            if portal:
                q = q.filter(JobRecord.source_portal == portal)
            if is_fresher is not None:
                q = q.filter(JobRecord.is_fresher_friendly == is_fresher)
                
            return q.count()

    def _to_record(self, job: ProcessedJob) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "fingerprint": job.fingerprint,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "is_remote": job.is_remote,
            "country": job.country,
            "city": job.city,
            "source_portal": job.source_portal,
            "portal_display_name": job.portal_display_name,
            "apply_url": job.apply_url,
            "job_type": job.job_type,
            "seniority": job.seniority,
            "domain": job.domain,
            "skills": job.skills,
            "qualifications": job.qualifications,
            "soft_skills": job.soft_skills,
            "salary_min": job.salary.min_value,
            "salary_max": job.salary.max_value,
            "salary_currency": job.salary.currency,
            "salary_period": job.salary.period,
            "salary_disclosed": job.salary.is_disclosed,
            "salary_raw": job.salary.raw,
            "posted_at": job.posted_at,
            "scraped_at": job.scraped_at,
            "processed_at": job.processed_at,
            "description_clean": job.description_clean,
            "description_summary": job.description_summary,
            "is_fresher_friendly": job.is_fresher_friendly,
            "requires_experience": job.requires_experience,
            "is_active": True,
        }

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        seniority: Optional[str] = None,
        is_remote: Optional[bool] = None,
        is_fresher: Optional[bool] = None,
        portal: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """Full-text search using PostgreSQL tsvector with optional filters."""
        with self.get_session() as session:
            # Check if search_vector column exists
            has_fulltext = session.execute(text("""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'jobs' AND column_name = 'search_vector'
            """)).fetchone() is not None
            
            if has_fulltext and query:
                # Use tsvector full-text search
                query_vector = plainto_tsquery('english', query)
                sql = """
                    SELECT *, ts_rank_cd(search_vector, plainto_tsquery('english', :query)) as rank_score
                    FROM jobs
                    WHERE search_vector @@ plainto_tsquery('english', :query)
                    AND is_active = true
                """
            else:
                # Fallback to ILIKE search or no query
                if query:
                    sql = """
                        SELECT *, 0.0 as rank_score
                        FROM jobs
                        WHERE (title ILIKE :query OR company ILIKE :query)
                        AND is_active = true
                    """
                else:
                    # No query - get all jobs
                    sql = """
                        SELECT *, 0.0 as rank_score
                        FROM jobs
                        WHERE is_active = true
                    """
            
            params = {"query": query, "limit": limit, "offset": offset}
            
            # Add optional filters
            if domain:
                sql += " AND domain = :domain"
                params["domain"] = domain
            if seniority:
                sql += " AND seniority = :seniority"
                params["seniority"] = seniority
            if is_remote is not None:
                sql += " AND is_remote = :is_remote"
                params["is_remote"] = is_remote
            if is_fresher is not None:
                sql += " AND is_fresher_friendly = :is_fresher"
                params["is_fresher"] = is_fresher
            if portal:
                sql += " AND source_portal = :portal"
                params["portal"] = portal
            
            # Order by rank (or scraped_at for fallback)
            if has_fulltext:
                sql += " ORDER BY rank_score DESC, scraped_at DESC"
            else:
                sql += " ORDER BY scraped_at DESC"
            
            sql += " LIMIT :limit OFFSET :offset"
            
            result = session.execute(text(sql), params).fetchall()
            
            # Convert to dicts with rank_score
            jobs = []
            for row in result:
                job_dict = dict(row._mapping)
                # Ensure rank_score is a float
                job_dict["rank_score"] = float(job_dict.get("rank_score", 0.0))
                jobs.append(job_dict)
            
            return jobs

    def count_search(
        self,
        query: str,
        domain: Optional[str] = None,
        seniority: Optional[str] = None,
        is_remote: Optional[bool] = None,
        is_fresher: Optional[bool] = None,
        portal: Optional[str] = None,
    ) -> int:
        """Count total results for a search query."""
        with self.get_session() as session:
            # Check if search_vector column exists
            has_fulltext = session.execute(text("""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'jobs' AND column_name = 'search_vector'
            """)).fetchone() is not None
            
            if has_fulltext:
                sql = """
                    SELECT COUNT(*)
                    FROM jobs
                    WHERE search_vector @@ plainto_tsquery('english', :query)
                    AND is_active = true
                """
            else:
                sql = """
                    SELECT COUNT(*)
                    FROM jobs
                    WHERE (title ILIKE :query OR company ILIKE :query)
                    AND is_active = true
                """
            
            params = {"query": f"%{query}%" if not has_fulltext else query}
            
            # Add optional filters
            if domain:
                sql += " AND domain = :domain"
                params["domain"] = domain
            if seniority:
                sql += " AND seniority = :seniority"
                params["seniority"] = seniority
            if is_remote is not None:
                sql += " AND is_remote = :is_remote"
                params["is_remote"] = is_remote
            if is_fresher is not None:
                sql += " AND is_fresher_friendly = :is_fresher"
                params["is_fresher"] = is_fresher
            if portal:
                sql += " AND source_portal = :portal"
                params["portal"] = portal
            
            result = session.execute(text(sql), params).scalar()
            return result or 0

    def get_job_count(self) -> int:
        """Get total active job count."""
        with self.get_session() as session:
            return session.query(JobRecord).filter(JobRecord.is_active == True).count() or 0
