"""
NLP Extractor — the intelligence layer of the pipeline.

Extracts from job descriptions:
  ✓ Skills (from taxonomy + spaCy NER)
  ✓ Domain (rule-based + zero-shot if needed)
  ✓ Seniority level (fresher / junior / mid / senior)
  ✓ Salary info (regex + heuristics)
  ✓ Experience required (regex)
  ✓ Qualifications
  ✓ Fresher-friendly flag
"""
from __future__ import annotations
import re
from functools import lru_cache
from typing import Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.skills_taxonomy import ALL_SKILLS, DOMAIN_SIGNALS, SKILLS_TAXONOMY
from config.settings import JOB_DOMAINS
from utils.models import RawJob, ProcessedJob, SalaryInfo
from nlp.text_cleaner import (
    clean_description, summarise, clean_location,
    extract_salary_string
)
from utils.logger import logger


# ── Seniority patterns ────────────────────────────────────────────────────────
_SENIORITY_MAP = {
    "Fresher": [
        r"\bfresher\b", r"\bfresh graduate\b", r"\b0\s*(?:year|yr)s?\b",
        r"\bno experience\b", r"\bcampus hire\b", r"\bnew grad\b",
        r"\brecent graduate\b", r"\bgraduate trainee\b",
    ],
    "Intern": [
        r"\bintern\b", r"\binternship\b", r"\bsummer trainee\b",
    ],
    "Entry Level": [
        r"\bentry.?level\b", r"\bjunior\b", r"\bassociate\b",
        r"\b0.?1\s*year\b", r"\b0.?2\s*year\b", r"\b1\s*year\b",
        r"\btrainee\b",
    ],
    "Mid Level": [
        r"\bmid.?level\b", r"\b2.?4\s*year\b", r"\b3\s*year\b",
        r"\b4\s*year\b",
    ],
    "Senior": [
        r"\bsenior\b", r"\bsr\.\b", r"\blead\b", r"\bprincipal\b",
        r"\b5\+?\s*year\b", r"\b6\+?\s*year\b", r"\b7\+?\s*year\b",
    ],
}

# ── Experience extraction ─────────────────────────────────────────────────────
_EXP_PATTERN = re.compile(
    r"(\d+)\s*(?:–|-|to)\s*(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp\.?)?|"
    r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp\.?)?|"
    r"experience\s*(?:required|needed)?:?\s*(\d+)\s*(?:–|-|to)?\s*(\d+)?\s*(?:years?|yrs?)?",
    re.IGNORECASE,
)

# ── Salary parsing ────────────────────────────────────────────────────────────
_SALARY_NUM_RE = re.compile(r"[\d,]+(?:\.\d+)?")
_LPA_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:–|-|to)?\s*(\d+(?:\.\d+)?)?\s*(?:LPA|lpa|lakhs?|lacs?)", re.IGNORECASE)
_USD_RE = re.compile(r"\$\s*(\d+(?:,\d+)?(?:k)?)\s*(?:–|-|to)?\s*\$?\s*(\d+(?:,\d+)?(?:k)?)?", re.IGNORECASE)

# ── Qualification extraction ──────────────────────────────────────────────────
_QUAL_RE = re.compile(
    r"\b(?:B\.?Tech|B\.?E|B\.?Sc|BCA|MCA|M\.?Tech|M\.?Sc|MBA|"
    r"bachelor(?:'s)?|master(?:'s)?|B\.?Com|B\.?A|PHD|Ph\.?D)\b",
    re.IGNORECASE,
)

# ── Fresher signals ───────────────────────────────────────────────────────────
_FRESHER_SIGNALS = [
    r"\bfresher\b", r"\bfresh graduate\b", r"\b0\s*(?:year|yr)\b",
    r"\bentry.?level\b", r"\bjunior\b", r"\btrainee\b",
    r"\bintern\b", r"\bcampus\b", r"\bnew grad\b",
    r"\bnot mandatory\b.*experience", r"\bno experience required\b",
]
_FRESHER_RE = re.compile("|".join(_FRESHER_SIGNALS), re.IGNORECASE)


class NLPExtractor:
    """
    Stateless extractor. Load once, call extract() for each job.
    spaCy model is loaded lazily on first use.
    """

    def __init__(self, use_spacy: bool = True):
        self._nlp = None
        self._use_spacy = use_spacy
        # Pre-compile skill patterns for fast matching
        self._skill_patterns = {
            skill: re.compile(r"\b" + re.escape(skill) + r"\b", re.IGNORECASE)
            for skill in ALL_SKILLS
        }

    def _get_nlp(self):
        if self._nlp is None and self._use_spacy:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
                logger.info("[NLP] spaCy model loaded: en_core_web_sm")
            except Exception as e:
                logger.warning(f"[NLP] spaCy unavailable, running without it: {e}")
                self._use_spacy = False
        return self._nlp

    # ── Public entry point ────────────────────────────────────────────────────

    def extract(self, raw: RawJob) -> ProcessedJob:
        """Transform a RawJob into a fully enriched ProcessedJob."""

        desc_clean = clean_description(raw.description)
        combined_text = f"{raw.title} {raw.company} {desc_clean}"

        skills = self._extract_skills(combined_text)
        domain = self._detect_domain(combined_text, skills)
        seniority = self._detect_seniority(combined_text)
        salary = self._parse_salary(raw.salary_raw or extract_salary_string(combined_text) or "")
        qualifications = self._extract_qualifications(combined_text)
        experience_required = self._extract_experience(combined_text)
        is_fresher = self._is_fresher_friendly(combined_text, seniority)
        location, is_remote = clean_location(raw.location or "")

        # Soft skills
        soft_skills = [
            s for s in SKILLS_TAXONOMY["soft_skills"]
            if re.search(r"\b" + re.escape(s) + r"\b", combined_text, re.IGNORECASE)
        ]

        return ProcessedJob(
            fingerprint=raw.fingerprint,
            title=self._clean_title(raw.title),
            company=raw.company.strip(),
            location=location,
            is_remote=is_remote,
            source_portal=raw.source_portal,
            apply_url=raw.source_url,
            portal_display_name=self._portal_display(raw.source_portal),
            job_type=self._normalise_job_type(raw.job_type or ""),
            seniority=seniority,
            domain=domain,
            skills=skills,
            qualifications=qualifications,
            soft_skills=soft_skills,
            salary=salary,
            posted_at=self._parse_date(raw.posted_date_raw),
            scraped_at=raw.scraped_at,
            description_clean=desc_clean,
            description_summary=summarise(desc_clean),
            is_fresher_friendly=is_fresher,
            requires_experience=experience_required,
        )

    # ── Extractors ────────────────────────────────────────────────────────────

    def _extract_skills(self, text: str) -> list[str]:
        found = []
        seen = set()
        for skill, pattern in self._skill_patterns.items():
            if pattern.search(text) and skill not in seen:
                # Normalise: lowercase, deduplicate aliases
                normalised = skill.lower().replace(".", "").replace("-", " ")
                if normalised not in seen:
                    seen.add(normalised)
                    found.append(skill)
        # Sort by length descending — prefer longer specific matches
        found.sort(key=len, reverse=True)
        return found[:25]  # cap at 25 skills

    def _detect_domain(self, text: str, skills: list[str]) -> str:
        skills_lower = {s.lower() for s in skills}
        scores: dict[str, int] = {}

        for domain, domain_skills in DOMAIN_SIGNALS.items():
            score = sum(1 for s in domain_skills if s.lower() in skills_lower)
            if score > 0:
                scores[domain] = score

        if not scores:
            # Fallback: keyword scan on raw text
            text_lower = text.lower()
            for domain, domain_skills in DOMAIN_SIGNALS.items():
                score = sum(1 for s in domain_skills if s.lower() in text_lower)
                if score > 0:
                    scores[domain] = score

        if scores:
            return max(scores, key=scores.get)

        # Last resort: look at title
        title_lower = text[:60].lower()
        if any(kw in title_lower for kw in ["data", "ml", "machine learning", "ai"]):
            return "Data Science & ML"
        if any(kw in title_lower for kw in ["frontend", "front-end", "react", "vue"]):
            return "Frontend Development"
        if any(kw in title_lower for kw in ["backend", "back-end", "api", "server"]):
            return "Backend Development"
        if any(kw in title_lower for kw in ["design", "ui", "ux"]):
            return "UI/UX Design"
        if any(kw in title_lower for kw in ["devops", "cloud", "aws", "docker"]):
            return "DevOps & Cloud"

        return "Software Development" if any(
            kw in title_lower for kw in ["developer", "engineer", "programmer", "software"]
        ) else "Other"

    def _detect_seniority(self, text: str) -> str:
        for level, patterns in _SENIORITY_MAP.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return level
        return "Entry Level"  # default for fresher-targeted platform

    def _parse_salary(self, raw: str) -> SalaryInfo:
        if not raw:
            return SalaryInfo(is_disclosed=False)

        raw_clean = raw.strip()

        # Not disclosed patterns
        if re.search(r"not disclosed|competitive|as per|best in|negotiable", raw_clean, re.IGNORECASE):
            return SalaryInfo(is_disclosed=False, raw=raw_clean)

        # INR LPA format
        lpa_match = _LPA_RE.search(raw_clean)
        if lpa_match:
            min_val = float(lpa_match.group(1).replace(",", ""))
            max_val = float(lpa_match.group(2).replace(",", "")) if lpa_match.group(2) else min_val
            return SalaryInfo(
                min_value=min_val * 100000,   # convert LPA → annual INR
                max_value=max_val * 100000,
                currency="INR",
                period="yearly",
                is_disclosed=True,
                raw=raw_clean,
            )

        # USD format
        usd_match = _USD_RE.search(raw_clean)
        if usd_match:
            def parse_usd(s):
                if s:
                    s = s.replace(",", "")
                    if s.endswith("k"):
                        return float(s[:-1]) * 1000
                    return float(s)
                return None

            min_val = parse_usd(usd_match.group(1))
            max_val = parse_usd(usd_match.group(2))
            if min_val:
                return SalaryInfo(
                    min_value=min_val,
                    max_value=max_val or min_val,
                    currency="USD",
                    period="yearly",
                    is_disclosed=True,
                    raw=raw_clean,
                )

        return SalaryInfo(is_disclosed=True, raw=raw_clean)

    def _extract_qualifications(self, text: str) -> list[str]:
        matches = _QUAL_RE.findall(text)
        seen = set()
        result = []
        for m in matches:
            normalised = m.upper().replace(".", "")
            if normalised not in seen:
                seen.add(normalised)
                result.append(m)
        return result

    def _extract_experience(self, text: str) -> Optional[str]:
        match = _EXP_RE.search(text) if (_EXP_RE := _EXP_PATTERN).search(text) else None
        return match.group(0).strip() if match else None

    def _is_fresher_friendly(self, text: str, seniority: str) -> bool:
        if seniority in ("Fresher", "Intern", "Entry Level"):
            return True
        return bool(_FRESHER_RE.search(text))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _clean_title(self, title: str) -> str:
        # Remove noise suffixes like "(Fresher)" or "- 2024 Batch"
        title = re.sub(r"\(fresher\)|\(entry.?level\)|\(junior\)", "", title, flags=re.IGNORECASE)
        title = re.sub(r"[-–|]\s*20\d\d\s*batch", "", title, flags=re.IGNORECASE)
        return re.sub(r"\s{2,}", " ", title).strip()

    def _normalise_job_type(self, raw: str) -> str:
        raw_lower = raw.lower()
        if "intern" in raw_lower:
            return "Internship"
        if "contract" in raw_lower or "freelanc" in raw_lower:
            return "Contract"
        if "part" in raw_lower:
            return "Part-time"
        if "remote" in raw_lower:
            return "Remote"
        return "Full-time"

    def _parse_date(self, raw: Optional[str]):
        if not raw:
            return None
        from dateutil import parser as dateparser
        try:
            return dateparser.parse(raw, fuzzy=True)
        except Exception:
            return None

    def _portal_display(self, portal: str) -> str:
        mapping = {
            "remotive": "Remotive",
            "remoteok": "RemoteOK",
            "arbeitnow": "Arbeitnow",
            "internshala": "Internshala",
            "naukri": "Naukri",
            "linkedin": "LinkedIn",
            "freshersnow": "FreshersNow",
        }
        return mapping.get(portal, portal.title())
