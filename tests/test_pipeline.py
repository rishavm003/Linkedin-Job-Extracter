"""
Tests for the Job Extractor pipeline.
Run with: pytest tests/test_pipeline.py -v
"""
import asyncio
import sys, os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Model tests ───────────────────────────────────────────────────────────────

class TestRawJob:
    def test_fingerprint_deterministic(self):
        from utils.models import RawJob
        job1 = RawJob(
            source_portal="test", source_url="https://test.com",
            title="Python Developer", company="Acme", description="test"
        )
        job2 = RawJob(
            source_portal="test", source_url="https://different.com",
            title="Python Developer", company="Acme", description="different"
        )
        # Same title + company + portal → same fingerprint
        assert job1.fingerprint == job2.fingerprint

    def test_fingerprint_different_portals(self):
        from utils.models import RawJob
        job1 = RawJob(source_portal="naukri", source_url="x", title="Dev", company="X", description="d")
        job2 = RawJob(source_portal="linkedin", source_url="x", title="Dev", company="X", description="d")
        assert job1.fingerprint != job2.fingerprint


# ── Text cleaner tests ────────────────────────────────────────────────────────

class TestTextCleaner:
    def test_strip_html(self):
        from nlp.text_cleaner import strip_html
        result = strip_html("<p>Hello <b>World</b></p>")
        assert "Hello" in result
        assert "<p>" not in result
        assert "<b>" not in result

    def test_clean_location_remote(self):
        from nlp.text_cleaner import clean_location
        loc, is_remote = clean_location("Remote / Worldwide")
        assert is_remote is True

    def test_clean_location_bangalore(self):
        from nlp.text_cleaner import clean_location
        loc, is_remote = clean_location("bengaluru, india")
        assert loc == "Bangalore"
        assert is_remote is False

    def test_salary_extraction(self):
        from nlp.text_cleaner import extract_salary_string
        text = "The salary offered is ₹3-5 LPA based on experience."
        result = extract_salary_string(text)
        assert result is not None
        assert "3" in result

    def test_summarise(self):
        from nlp.text_cleaner import summarise
        long_text = "We are a tech company. " * 50
        summary = summarise(long_text, max_chars=350)
        assert len(summary) <= 360


# ── NLP Extractor tests ───────────────────────────────────────────────────────

class TestNLPExtractor:
    @pytest.fixture
    def extractor(self):
        from nlp.extractor import NLPExtractor
        return NLPExtractor(use_spacy=False)

    @pytest.fixture
    def sample_raw(self):
        from utils.models import RawJob
        return RawJob(
            source_portal="test",
            source_url="https://test.com/job/1",
            title="Junior Python Developer (Fresher Welcome)",
            company="TechStartup",
            location="Bangalore",
            description="""
            Hiring a fresher Python developer.
            Skills needed: Python, Django, PostgreSQL, REST APIs.
            Qualification: B.Tech in Computer Science.
            Experience: 0-1 years.
            Salary: ₹3-4 LPA.
            Remote friendly.
            """,
            salary_raw="₹3-4 LPA",
        )

    def test_skill_extraction(self, extractor, sample_raw):
        result = extractor.extract(sample_raw)
        skills_lower = [s.lower() for s in result.skills]
        assert "python" in skills_lower
        assert "postgresql" in skills_lower or "django" in skills_lower

    def test_domain_detection(self, extractor, sample_raw):
        result = extractor.extract(sample_raw)
        assert result.domain in ("Software Development", "Backend Development", "Full Stack Development")

    def test_seniority_fresher(self, extractor, sample_raw):
        result = extractor.extract(sample_raw)
        assert result.seniority in ("Fresher", "Entry Level", "Intern")

    def test_fresher_flag(self, extractor, sample_raw):
        result = extractor.extract(sample_raw)
        assert result.is_fresher_friendly is True

    def test_salary_inr(self, extractor, sample_raw):
        result = extractor.extract(sample_raw)
        assert result.salary.is_disclosed is True
        assert result.salary.currency == "INR"
        assert result.salary.min_value == pytest.approx(300000.0)

    def test_remote_detection(self, extractor, sample_raw):
        result = extractor.extract(sample_raw)
        # "Remote friendly" is in description
        assert result.is_remote is True

    def test_qualification_extraction(self, extractor, sample_raw):
        result = extractor.extract(sample_raw)
        assert len(result.qualifications) > 0


# ── Deduplicator tests ────────────────────────────────────────────────────────

class TestDeduplicator:
    def _make_job(self, title, company, skills=None) -> "ProcessedJob":
        from utils.models import ProcessedJob, RawJob, SalaryInfo
        raw = RawJob(source_portal="test", source_url="x", title=title, company=company, description="d")
        return ProcessedJob(
            fingerprint=raw.fingerprint,
            title=title,
            company=company,
            source_portal="test",
            apply_url="x",
            portal_display_name="Test",
            skills=skills or [],
            salary=SalaryInfo(),
            description_clean="test",
            description_summary="test",
        )

    def test_exact_dedup(self):
        from nlp.deduplicator import Deduplicator
        dedup = Deduplicator()
        jobs = [
            self._make_job("Python Dev", "Acme"),
            self._make_job("Python Dev", "Acme"),  # exact duplicate
            self._make_job("Java Dev", "Acme"),
        ]
        result = dedup.deduplicate(jobs)
        assert len(result) == 2

    def test_fuzzy_dedup(self):
        from nlp.deduplicator import Deduplicator
        dedup = Deduplicator(fuzzy_threshold=85.0)
        jobs = [
            self._make_job("Junior Python Developer", "TechCorp"),
            self._make_job("Junior Python Developer (Fresher)", "TechCorp"),  # near-duplicate
            self._make_job("Senior Java Engineer", "OtherCo"),
        ]
        result = dedup.deduplicate(jobs)
        assert len(result) == 2


# ── API-based scraper smoke tests ─────────────────────────────────────────────
# These hit live APIs — mark them to run only when LIVE_TEST=1

@pytest.mark.skipif(os.getenv("LIVE_TEST") != "1", reason="Live API test, set LIVE_TEST=1")
class TestLiveScrapers:
    def test_remotive_live(self):
        from scrapers.remotive_scraper import RemotiveScraper
        async def _run():
            async with RemotiveScraper() as s:
                return await s.scrape(max_jobs=5)
        jobs = asyncio.run(_run())
        assert len(jobs) > 0
        assert jobs[0].title
        assert jobs[0].source_url.startswith("http")

    def test_remoteok_live(self):
        from scrapers.remoteok_scraper import RemoteOKScraper
        async def _run():
            async with RemoteOKScraper() as s:
                return await s.scrape(max_jobs=5)
        jobs = asyncio.run(_run())
        assert len(jobs) > 0

    def test_arbeitnow_live(self):
        from scrapers.arbeitnow_scraper import ArbeitnowScraper
        async def _run():
            async with ArbeitnowScraper() as s:
                return await s.scrape(max_jobs=5)
        jobs = asyncio.run(_run())
        assert len(jobs) > 0
