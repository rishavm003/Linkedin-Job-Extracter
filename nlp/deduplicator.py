"""
Deduplication engine.

Two-stage approach:
  1. Fast: SHA-256 fingerprint (exact dedup — same title + company + portal)
  2. Fuzzy: RapidFuzz Levenshtein on title+company for near-duplicates
             across different portals (same job posted on LinkedIn AND Naukri)

Optional Stage 3: Sentence-transformer embeddings for semantic dedup
(disabled by default — needs more compute, enable for production).
"""
from __future__ import annotations
import hashlib
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rapidfuzz import fuzz, process
from utils.models import ProcessedJob
from utils.logger import logger
from config.settings import SIMILARITY_THRESHOLD


class Deduplicator:
    """
    Deduplicates a list of ProcessedJob records.
    Call deduplicate(jobs) → unique jobs list.
    """

    def __init__(
        self,
        fuzzy_threshold: float = 88.0,   # 0–100, higher = stricter
        use_embeddings: bool = False,     # set True in production for cross-portal dedup
    ):
        self.fuzzy_threshold = fuzzy_threshold
        self.use_embeddings = use_embeddings
        self._embed_model = None

    def deduplicate(self, jobs: list[ProcessedJob]) -> list[ProcessedJob]:
        """
        Full deduplication pipeline. Returns unique jobs.
        """
        logger.info(f"[Dedup] Input: {len(jobs)} jobs")

        # Stage 1: fingerprint dedup
        after_fp = self._fingerprint_dedup(jobs)
        logger.info(f"[Dedup] After fingerprint dedup: {len(after_fp)} jobs")

        # Stage 2: fuzzy dedup (cross-portal)
        after_fuzzy = self._fuzzy_dedup(after_fp)
        logger.info(f"[Dedup] After fuzzy dedup: {len(after_fuzzy)} jobs")

        # Stage 3: embedding dedup (optional)
        if self.use_embeddings:
            after_embed = self._embedding_dedup(after_fuzzy)
            logger.info(f"[Dedup] After embedding dedup: {len(after_embed)} jobs")
            return after_embed

        return after_fuzzy

    def _fingerprint_dedup(self, jobs: list[ProcessedJob]) -> list[ProcessedJob]:
        seen: set[str] = set()
        unique: list[ProcessedJob] = []
        for job in jobs:
            if job.fingerprint not in seen:
                seen.add(job.fingerprint)
                unique.append(job)
        return unique

    def _job_key(self, job: ProcessedJob) -> str:
        """String used for fuzzy comparison."""
        return f"{job.title.lower()} {job.company.lower()}"

    def _fuzzy_dedup(self, jobs: list[ProcessedJob]) -> list[ProcessedJob]:
        if not jobs:
            return jobs

        unique: list[ProcessedJob] = []
        unique_keys: list[str] = []

        for job in jobs:
            key = self._job_key(job)

            if not unique_keys:
                unique.append(job)
                unique_keys.append(key)
                continue

            # Check against all existing unique job keys
            best_match = process.extractOne(
                key,
                unique_keys,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=self.fuzzy_threshold,
            )

            if best_match is None:
                # No close match found — it's unique
                unique.append(job)
                unique_keys.append(key)
            else:
                # Near-duplicate found — keep the one with more data
                matched_idx = unique_keys.index(best_match[0])
                existing = unique[matched_idx]

                # Prefer the job with a longer description (more info)
                if len(job.description_clean) > len(existing.description_clean):
                    unique[matched_idx] = job
                    unique_keys[matched_idx] = key

        return unique

    def _embedding_dedup(self, jobs: list[ProcessedJob]) -> list[ProcessedJob]:
        """
        Semantic deduplication using embeddings.
        First tries sentence-transformers, falls back to TF-IDF if unavailable.
        """
        # Try sentence-transformers first (better quality, but requires torch)
        try:
            return self._sentence_transformer_dedup(jobs)
        except ImportError:
            logger.info("[Dedup] sentence-transformers not available, using TF-IDF fallback")
        
        # Fallback to TF-IDF (lightweight, scikit-learn only)
        return self._tfidf_dedup(jobs)

    def _sentence_transformer_dedup(self, jobs: list[ProcessedJob]) -> list[ProcessedJob]:
        """Semantic dedup using sentence-transformers (requires torch)."""
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        if self._embed_model is None:
            logger.info("[Dedup] Loading sentence-transformer model...")
            self._embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        texts = [f"{j.title} {j.company} {j.description_summary}" for j in jobs]
        embeddings = self._embed_model.encode(texts, batch_size=64, show_progress_bar=False)
        
        return self._cosine_sim_filter(jobs, embeddings)

    def _tfidf_dedup(self, jobs: list[ProcessedJob]) -> list[ProcessedJob]:
        """Lightweight semantic dedup using TF-IDF vectors (scikit-learn only)."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            logger.warning("[Dedup] scikit-learn not installed — skipping embedding dedup")
            return jobs
        
        logger.info("[Dedup] Using TF-IDF for semantic deduplication (lightweight)")
        
        # Combine job features into text representation
        texts = []
        for j in jobs:
            skills_text = " ".join(j.skills[:10])  # top 10 skills
            text = f"{j.title} {j.company} {j.domain} {skills_text} {j.description_summary[:200]}"
            texts.append(text.lower())
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=1000,  # Limit features for speed
            stop_words='english',
            ngram_range=(1, 2),  # unigrams and bigrams
            min_df=1,  # include terms that appear at least once
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            embeddings = tfidf_matrix.toarray()
        except ValueError:
            # If vocabulary is empty or other issues, skip dedup
            logger.warning("[Dedup] TF-IDF vectorization failed — skipping embedding dedup")
            return jobs
        
        return self._cosine_sim_filter(jobs, embeddings)

    def _cosine_sim_filter(self, jobs: list[ProcessedJob], embeddings) -> list[ProcessedJob]:
        """Filter jobs based on cosine similarity of embeddings."""
        from sklearn.metrics.pairwise import cosine_similarity
        
        sim_matrix = cosine_similarity(embeddings)
        
        keep = [True] * len(jobs)
        for i in range(len(jobs)):
            if not keep[i]:
                continue
            for j in range(i + 1, len(jobs)):
                if keep[j] and sim_matrix[i][j] >= SIMILARITY_THRESHOLD:
                    # Keep the one with more skills extracted
                    if len(jobs[i].skills) >= len(jobs[j].skills):
                        keep[j] = False
                    else:
                        keep[i] = False
                        break
        
        return [job for job, k in zip(jobs, keep) if k]
