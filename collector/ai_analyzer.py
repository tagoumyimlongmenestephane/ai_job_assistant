"""Deterministically analyze job listings against the candidate profile.

This is a local simulation: it finds skills in the job listing text and
calculates a simple relevance level.
"""

from collections.abc import Iterable, Mapping
import re


USER_PROFILE = {
    "education": ["Informatique", "Applied Data Science"],
    "skills": [
        "Python",
        "Django",
        "React",
        "PHP",
        "Flutter",
        "Git",
        "JavaScript",
        "SQL",
        "HTML",
        "CSS",
        "Figma",
        "Linux",
        "AWS",
        "n8n",
        "Docker",
        "MySQL",
        "PostgreSQL",
    ],
    "experience": ["Stage chez THE NET Enterprise"],
    "languages": ["Français", "Allemand", "Anglais"],
    "career_goal": "Développement logiciel, Data Science, Software Engineering",
}

RELEVANCE_THRESHOLDS = {"high": 0.5, "medium": 0.2}
RECOMMENDATIONS = {
    "HIGH": "APPLY",
    "MEDIUM": "REVIEW",
    "LOW": "LOW_PRIORITY",
    "UNKNOWN": "REVIEW",
}


def extract_job_text(job: Mapping) -> str:
    """Build the text to analyze from the job listing fields."""
    parts = (job.get("title"), job.get("description"), job.get("company"))
    return " ".join(value for value in parts if isinstance(value, str)).casefold()


def _contains_skill(text: str, skill: str) -> bool:
    """Find a skill as a standalone term to avoid false positives."""
    pattern = rf"(?<!\w){re.escape(skill.casefold())}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def find_skills(text: str, skills: Iterable[str] | None = None) -> list[str]:
    """Return the mentioned skills in profile order."""
    candidates = USER_PROFILE["skills"] if skills is None else skills
    normalized_text = text.casefold()
    return [skill for skill in candidates if _contains_skill(normalized_text, skill)]


def calculate_relevance(matched_skills: Iterable[str], skills: Iterable[str] | None = None) -> str:
    """Classify the share of profile skills found in the job listing."""
    profile_skills = list(USER_PROFILE["skills"] if skills is None else skills)
    if not profile_skills:
        return "UNKNOWN"

    matched = set(matched_skills)
    ratio = sum(skill in matched for skill in profile_skills) / len(profile_skills)
    if ratio >= RELEVANCE_THRESHOLDS["high"]:
        return "HIGH"
    if ratio >= RELEVANCE_THRESHOLDS["medium"]:
        return "MEDIUM"
    return "LOW"


def analyze_job_simulated(job: Mapping) -> dict:
    """Analyze a job listing and return a JSON-serializable result."""
    skills = USER_PROFILE["skills"]
    matched_skills = find_skills(extract_job_text(job), skills)
    matched_set = set(matched_skills)
    missing_skills = [skill for skill in skills if skill not in matched_set]
    relevance = calculate_relevance(matched_skills, skills)

    return {
        "reference": job.get("reference"),
        "title": job.get("title"),
        "company": job.get("company"),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "profile_relevance": relevance,
        "recommendation": RECOMMENDATIONS[relevance],
        "analysis_mode": "SIMULATION",
    }


def analyze_jobs_simulated(jobs: Iterable[Mapping]) -> list[dict]:
    """Analyze multiple job listings while preserving their input order."""
    return [analyze_job_simulated(job) for job in jobs]
