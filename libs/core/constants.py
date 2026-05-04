# ── Portal targets (freshers / entry-level focused) ───────────────────────────
PORTALS = {
    "remotive": {
        "enabled": True,
        "base_url": "https://remotive.com/api/remote-jobs",
        "type": "api",
    },
    "remoteok": {
        "enabled": True,
        "base_url": "https://remoteok.com/api",
        "type": "api",
    },
    "github_jobs_archive": {
        "enabled": True,
        "base_url": "https://www.arbeitnow.com/api/job-board-api",
        "type": "api",
    },
    "internshala": {
        "enabled": True,
        "base_url": "https://internshala.com/internships",
        "type": "scraper",
    },
    "naukri": {
        "enabled": True,
        "base_url": "https://www.naukri.com/jobs-in-india",
        "type": "scraper",
    },
    "indeed": {
        "enabled": True,
        "base_url": "https://www.indeed.com/jobs",
        "type": "scraper",
    },
    "linkedin": {
        "enabled": True,
        "base_url": "https://www.linkedin.com/jobs/search",
        "type": "scraper",
    },
    "wellfound": {
        "enabled": True,
        "base_url": "https://wellfound.com/jobs",
        "type": "scraper",
    },
    "freshersnow": {
        "enabled": True,
        "base_url": "https://freshersnow.com/category/freshers-jobs/",
        "type": "scraper",
    },
}

# ── Search keywords for fresher jobs ─────────────────────────────────────────
FRESHER_KEYWORDS = [
    "fresher", "entry level", "0-1 years", "0-2 years",
    "junior", "trainee", "intern", "graduate", "campus hire",
    "recent graduate", "new grad",
]

JOB_DOMAINS = [
    "Software Development",
    "Data Science & ML",
    "DevOps & Cloud",
    "Frontend Development",
    "Backend Development",
    "Full Stack Development",
    "Mobile Development",
    "Cybersecurity",
    "UI/UX Design",
    "Product Management",
    "Data Analysis",
    "Digital Marketing",
    "Content Writing",
    "Finance & Accounting",
    "HR & Recruitment",
    "Customer Support",
    "Sales",
    "Operations",
    "Research",
    "Other",
]
