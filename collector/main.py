"""Entry point for the job collection and analysis pipeline."""

import json
from pathlib import Path

from ai_analyzer import analyze_jobs_simulated
from match import match_jobs
from normalizer import normalize_jobs


JOBS_FILE = Path(__file__).parent / "sources" / "jobs_test.json"


def main() -> None:
    with JOBS_FILE.open(encoding="utf-8") as file:
        raw_jobs = json.load(file)

    print("Offres récupérées :", len(raw_jobs.get("ergebnisliste", [])))

    clean_jobs = normalize_jobs(raw_jobs)
    print("Offres après nettoyage :", len(clean_jobs))

    matched_jobs = match_jobs(clean_jobs)
    analyses = analyze_jobs_simulated(matched_jobs)

    for job, analysis in zip(matched_jobs, analyses):
        print("\n---------------------------")
        print("Poste :", job.get("title"))
        print("Entreprise :", job.get("company"))
        print("Score matching :", job.get("match_score"))
        print("Classification :", job.get("classification"))
        print("Compétences trouvées :", analysis["matched_skills"])
        print("Compétences manquantes :", analysis["missing_skills"])
        print("Recommandation IA :", analysis["recommendation"])


if __name__ == "__main__":
    main()
