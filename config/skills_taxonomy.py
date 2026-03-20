"""
Skill taxonomy used by the NLP extractor.
Organised by domain so we can auto-tag jobs even without a classifier.
"""

SKILLS_TAXONOMY = {

    # ── Programming languages ─────────────────────────────────────────────────
    "languages": [
        "python", "javascript", "typescript", "java", "kotlin", "swift",
        "c", "c++", "c#", "go", "golang", "rust", "ruby", "php", "scala",
        "r", "matlab", "perl", "bash", "shell", "powershell", "dart",
        "elixir", "haskell", "lua", "groovy", "objective-c",
    ],

    # ── Web frontend ─────────────────────────────────────────────────────────
    "frontend": [
        "react", "react.js", "reactjs", "next.js", "nextjs", "vue", "vue.js",
        "angular", "svelte", "nuxt", "gatsby", "html", "html5", "css", "css3",
        "sass", "scss", "less", "tailwind", "tailwindcss", "bootstrap",
        "material ui", "mui", "chakra ui", "styled-components", "webpack",
        "vite", "babel", "jquery", "redux", "zustand", "graphql", "apollo",
    ],

    # ── Web backend ──────────────────────────────────────────────────────────
    "backend": [
        "node.js", "nodejs", "express", "express.js", "fastapi", "django",
        "flask", "spring", "spring boot", "laravel", "rails", "ruby on rails",
        "asp.net", ".net", "nest.js", "nestjs", "hapi", "koa", "gin",
        "fiber", "actix", "rocket", "phoenix", "aiohttp", "tornado",
    ],

    # ── Databases ────────────────────────────────────────────────────────────
    "databases": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis",
        "elasticsearch", "cassandra", "dynamodb", "firebase", "supabase",
        "oracle", "sql server", "mssql", "mariadb", "neo4j", "influxdb",
        "cockroachdb", "planetscale", "prisma", "sqlalchemy", "mongoose",
        "sequelize", "typeorm", "sql", "nosql",
    ],

    # ── Cloud & DevOps ───────────────────────────────────────────────────────
    "devops_cloud": [
        "aws", "amazon web services", "gcp", "google cloud", "azure",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins",
        "github actions", "gitlab ci", "circleci", "travis ci",
        "nginx", "apache", "linux", "ubuntu", "debian", "helm",
        "prometheus", "grafana", "datadog", "splunk", "elk stack",
        "ci/cd", "devops", "sre", "site reliability",
    ],

    # ── Data science & ML ────────────────────────────────────────────────────
    "data_ml": [
        "machine learning", "ml", "deep learning", "dl", "artificial intelligence",
        "ai", "nlp", "natural language processing", "computer vision", "cv",
        "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
        "jupyter", "huggingface", "transformers", "llm", "langchain",
        "xgboost", "lightgbm", "catboost", "opencv", "yolo",
        "spark", "hadoop", "hive", "airflow", "mlflow", "dvc",
        "data analysis", "data science", "data engineering", "etl",
        "power bi", "tableau", "looker", "data visualization",
        "statistics", "probability", "linear algebra",
    ],

    # ── Mobile ───────────────────────────────────────────────────────────────
    "mobile": [
        "android", "ios", "flutter", "react native", "xamarin",
        "swift", "swiftui", "kotlin", "java android", "ionic",
        "expo", "capacitor",
    ],

    # ── Cybersecurity ────────────────────────────────────────────────────────
    "security": [
        "cybersecurity", "penetration testing", "ethical hacking",
        "network security", "vulnerability assessment", "soc", "siem",
        "firewall", "encryption", "ssl", "tls", "owasp", "burp suite",
        "nmap", "metasploit", "wireshark", "kali linux",
    ],

    # ── Design ───────────────────────────────────────────────────────────────
    "design": [
        "ui design", "ux design", "ui/ux", "figma", "adobe xd", "sketch",
        "invision", "photoshop", "illustrator", "after effects", "canva",
        "prototyping", "wireframing", "user research", "design thinking",
    ],

    # ── Soft skills (used for JD summary, not domain tagging) ────────────────
    "soft_skills": [
        "communication", "teamwork", "problem solving", "analytical",
        "leadership", "time management", "adaptability", "creativity",
        "critical thinking", "collaboration", "attention to detail",
        "self-motivated", "fast learner",
    ],

    # ── Qualifications (fresher-relevant) ────────────────────────────────────
    "qualifications": [
        "b.tech", "btech", "b.e", "be", "b.sc", "bsc", "mca", "bca",
        "m.tech", "mtech", "m.sc", "msc", "mba", "bachelor", "master",
        "computer science", "information technology", "it", "cse",
        "ece", "eee", "mechanical", "civil", "electronics",
        "cgpa", "gpa", "percentage", "aggregate",
    ],
}

# Flat list for fast lookup
ALL_SKILLS: list[str] = []
for _skills in SKILLS_TAXONOMY.values():
    ALL_SKILLS.extend(_skills)

# Domain → skill mapping (for auto domain-tagging)
DOMAIN_SIGNALS: dict[str, list[str]] = {
    "Data Science & ML":      SKILLS_TAXONOMY["data_ml"],
    "Frontend Development":   SKILLS_TAXONOMY["frontend"],
    "Backend Development":    SKILLS_TAXONOMY["backend"],
    "DevOps & Cloud":         SKILLS_TAXONOMY["devops_cloud"],
    "Mobile Development":     SKILLS_TAXONOMY["mobile"],
    "Cybersecurity":          SKILLS_TAXONOMY["security"],
    "UI/UX Design":           SKILLS_TAXONOMY["design"],
}
