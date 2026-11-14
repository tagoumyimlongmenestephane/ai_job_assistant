
"""Entry point for the job collection and analysis pipeline."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from collector.job_fetcher import fetch_all_jobs
from collector.ai_analyzer import analyze_jobs_simulated
from collector.match import match_jobs
from collector.normalizer import normalize_jobs
from collector.reports import (
    export_jobs_csv,
    export_jobs_excel,
    generate_global_report,
    generate_top_jobs_report,
    generate_contract_report
)

from db import (
    get_job_id,
    save_analysis,
    save_source,
    save_jobs,
    get_connection
)

SOURCE_NAME = "Bundesagentur für Arbeit"
SOURCE_URL = "https://www.arbeitsagentur.de"


def main():

    conn = get_connection()
    # 1. Fetch live jobs from the API

    try:
        raw_jobs = fetch_all_jobs()

    except Exception as error:
        print("Erreur pendant la récupération des offres :", error)
        return

    raw_job_list = raw_jobs.get("ergebnisliste", [])


    if not raw_job_list:
        print("Aucune offre trouvée. Arrêt du programme.")
        return

    # 2. Normalize jobs

    clean_jobs = normalize_jobs(raw_jobs)


    if not clean_jobs:
        print("Aucune offre valide à traiter.")
        return

    # 3. Save source in PostgreSQL
    print("\n[3/7] Identification de la source...")

    source_id = save_source(SOURCE_NAME, SOURCE_URL)

    print("Source ID :", source_id)

    # 4. Save jobs in PostgreSQL

    saved_count = save_jobs(clean_jobs, source_id)


    # 5. Match jobs

    matched_jobs = match_jobs(clean_jobs)


    # 6. AI analysis
    print("\n[6/7] Analyse IA...")

    analyses = analyze_jobs_simulated(matched_jobs)

    # 7. Save analyses

    for job, analysis in zip(matched_jobs, analyses):

        job_id = get_job_id(source_id, job["reference"])

        if job_id is None:
            print(
                f"Impossible de retrouver l'offre : "
                f"{job.get('reference')}"
            )
            continue

        save_analysis(job_id, job, analysis)

    print("\nToutes les opérations sont terminées !")

    # Display results
    for job, analysis in zip(matched_jobs, analyses):

        print("\n---------------------------")
        print("Poste :", job.get("title"))
        print("Entreprise :", job.get("company"))
        print("Ville :", job.get("city"))
        print("Distance :", job.get("distance_km"), "km")
        print(
            "Salaire :",
            job.get("salary_min"),
            "-",
            job.get("salary_max"),
            job.get("pay_unit")
        )
        print("Score matching :", job.get("match_score"))
        print("Classification :", job.get("classification"))
        print("Compétences trouvées :", analysis.get("matched_skills"))
        print("Compétences manquantes :", analysis.get("missing_skills"))
        print("Recommandation IA :", analysis.get("recommendation"))

    try:
        generate_global_report(conn)
        generate_top_jobs_report(conn)
        generate_contract_report(conn)
        export_jobs_csv(conn)
        export_jobs_excel(conn)
    except Exception as error:
        print("Erreur lors de la génération des rapports :", error)
    finally:
        conn.close()


main()
