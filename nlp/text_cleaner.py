"""
Text cleaning utilities.
Strips HTML, normalises whitespace, removes boilerplate from job descriptions.
"""
from __future__ import annotations
import re
import html
from bs4 import BeautifulSoup


# Patterns for salary ranges in Indian and international formats
_SALARY_PATTERNS = [
    # INR formats
    r"₹\s*[\d,]+\s*(?:–|-|to)\s*₹?\s*[\d,]+\s*(?:LPA|lpa|L|lakhs?|lacs?|per annum)?",
    r"INR\s*[\d,]+\s*(?:–|-|to)\s*[\d,]+",
    r"Rs\.?\s*[\d,]+\s*(?:–|-|to)\s*[\d,]+\s*(?:LPA|lpa|per annum|per month|PM)?",
    r"[\d,]+\s*(?:LPA|lpa|L|lakhs?|lacs?)",
    # USD formats
    r"\$\s*[\d,]+\s*(?:–|-|to)\s*\$?\s*[\d,]+\s*(?:per year|per hour|per month|annually)?",
    r"USD\s*[\d,]+\s*(?:–|-|to)\s*[\d,]+",
    # Generic
    r"Salary:?\s*(?:Not Disclosed|Competitive|As per industry|Best in industry)",
    r"CTC:?\s*[\d,.]+\s*(?:–|-|to)?\s*[\d,.]*\s*(?:LPA|lpa)?",
]

_SALARY_RE = re.compile("|".join(_SALARY_PATTERNS), re.IGNORECASE)

# Boilerplate phrases common in JDs — remove for cleaner NLP
_BOILERPLATE = [
    r"equal opportunity employer",
    r"we are an equal",
    r"diversity and inclusion",
    r"apply now",
    r"click here to apply",
    r"send your resume",
    r"email your cv",
    r"note:\s*only shortlisted candidates",
    r"no of openings?:?\s*\d+",
    r"walk.in interview",
    r"disclaimer",
]
_BOILERPLATE_RE = re.compile("|".join(_BOILERPLATE), re.IGNORECASE)


def strip_html(text: str) -> str:
    """Remove all HTML tags and decode HTML entities."""
    if not text:
        return ""
    text = html.unescape(text)
    soup = BeautifulSoup(text, "lxml")
    return soup.get_text(separator=" ")


def normalise_whitespace(text: str) -> str:
    """Collapse all whitespace runs to a single space."""
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+|www\.\S+", "", text)


def remove_boilerplate(text: str) -> str:
    return _BOILERPLATE_RE.sub("", text)


def extract_salary_string(text: str) -> str | None:
    """Pull the first salary mention out of raw text."""
    match = _SALARY_RE.search(text)
    return match.group(0).strip() if match else None


def clean_description(raw: str) -> str:
    """
    Full cleaning pipeline for a job description.
    Returns clean, normalised plain text suitable for NLP.
    """
    text = strip_html(raw)
    text = remove_urls(text)
    text = remove_boilerplate(text)
    text = normalise_whitespace(text)
    return text


def summarise(text: str, max_chars: int = 350) -> str:
    """Return the first sentence(s) up to max_chars as a summary."""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    # Try to cut at a sentence boundary
    cut = text[:max_chars]
    last_period = cut.rfind(". ")
    if last_period > 100:
        return cut[:last_period + 1].strip()
    return cut.rstrip(",; ") + "…"


def clean_location(raw: str) -> tuple[str, bool]:
    """
    Normalise location string and detect remote.
    Returns (cleaned_location, is_remote).
    """
    if not raw:
        return "India", False

    raw_lower = raw.lower()
    is_remote = any(kw in raw_lower for kw in [
        "remote", "work from home", "wfh", "anywhere", "worldwide", "global"
    ])

    # Standardise common aliases
    replacements = {
        "bengaluru": "Bangalore",
        "bengalure": "Bangalore",
        "new delhi": "Delhi",
        "ncr": "Delhi NCR",
        "mumbai": "Mumbai",
        "hyderabad": "Hyderabad",
        "pune": "Pune",
        "chennai": "Chennai",
        "kolkata": "Kolkata",
    }

    cleaned = raw.strip()
    for alias, standard in replacements.items():
        if alias in raw_lower:
            cleaned = standard
            break

    # Remove noise suffixes
    cleaned = re.sub(r",?\s*(india|in|us|usa|uk)\s*$", "", cleaned, flags=re.IGNORECASE).strip()

    if not cleaned:
        cleaned = "Remote" if is_remote else "India"

    return cleaned, is_remote
