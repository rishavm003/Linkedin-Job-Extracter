"""
NLP Pipeline — ties together cleaning, extraction, and deduplication.
Input:  list[RawJob]
Output: list[ProcessedJob]
"""
from __future__ import annotations
import asyncio
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm
from utils.models import RawJob, ProcessedJob
from nlp.extractor import NLPExtractor
from nlp.deduplicator import Deduplicator
from utils.logger import logger


def _extract_single(raw_dict: dict) -> dict | None:
    """
    Top-level function (must be picklable for ProcessPoolExecutor).
    Receives a RawJob as dict, returns ProcessedJob as dict.
    """
    try:
        extractor = NLPExtractor(use_spacy=False)  # no spaCy in subprocess
        raw = RawJob(**raw_dict)
        processed = extractor.extract(raw)
        return processed.model_dump()
    except Exception as e:
        return None


class NLPPipeline:
    """
    Processes a batch of RawJobs through the full NLP pipeline.
    Uses multiprocessing for CPU-bound extraction.
    """

    def __init__(
        self,
        use_multiprocessing: bool = True,
        max_workers: int = 4,
        use_embeddings: bool = False,
    ):
        self.use_multiprocessing = use_multiprocessing
        self.max_workers = max_workers
        self.deduplicator = Deduplicator(use_embeddings=use_embeddings)
        self._extractor = NLPExtractor(use_spacy=True)

    def run(self, raw_jobs: list[RawJob]) -> list[ProcessedJob]:
        """
        Full pipeline: clean → extract → deduplicate.
        Returns list of ProcessedJob ready for storage.
        """
        if not raw_jobs:
            logger.warning("[NLP Pipeline] No raw jobs to process.")
            return []

        logger.info(f"[NLP Pipeline] Processing {len(raw_jobs)} raw jobs...")

        processed: list[ProcessedJob] = []
        failed = 0

        if self.use_multiprocessing and len(raw_jobs) > 20:
            processed, failed = self._run_parallel(raw_jobs)
        else:
            processed, failed = self._run_sequential(raw_jobs)

        logger.info(f"[NLP Pipeline] Extracted {len(processed)} jobs ({failed} failed)")

        # Deduplication
        unique = self.deduplicator.deduplicate(processed)
        logger.info(f"[NLP Pipeline] ✓ Final unique jobs: {len(unique)}")

        return unique

    def _run_sequential(self, raw_jobs: list[RawJob]) -> tuple[list[ProcessedJob], int]:
        processed = []
        failed = 0
        for raw in tqdm(raw_jobs, desc="Extracting", unit="job"):
            try:
                result = self._extractor.extract(raw)
                processed.append(result)
            except Exception as e:
                logger.warning(f"[NLP Pipeline] Extraction failed for '{raw.title}': {e}")
                failed += 1
        return processed, failed

    def _run_parallel(self, raw_jobs: list[RawJob]) -> tuple[list[ProcessedJob], int]:
        processed = []
        failed = 0
        raw_dicts = [job.model_dump() for job in raw_jobs]

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(_extract_single, rd): rd for rd in raw_dicts}
            with tqdm(total=len(futures), desc="Extracting (parallel)", unit="job") as pbar:
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            processed.append(ProcessedJob(**result))
                        else:
                            failed += 1
                    except Exception as e:
                        logger.warning(f"[NLP Pipeline] Worker error: {e}")
                        failed += 1
                    finally:
                        pbar.update(1)

        return processed, failed

    def process_single(self, raw: RawJob) -> Optional[ProcessedJob]:
        """Process a single job (useful for testing)."""
        try:
            return self._extractor.extract(raw)
        except Exception as e:
            logger.error(f"[NLP Pipeline] Single extraction failed: {e}")
            return None
