import os
import json
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def test_connection():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database();")
                database = cur.fetchone()

                print("Connexion réussie !")
                print("Base connectée :", database[0])

    except Exception as error:
        print("Erreur de connexion :", error)


if __name__ == "__main__":
    test_connection()

def save_source(name, base_url):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sources (name, base_url)
                VALUES (%s, %s)
                ON CONFLICT (name)
                DO UPDATE SET base_url = EXCLUDED.base_url
                RETURNING id;
            """, (name, base_url))

            source_id = cur.fetchone()[0]

    return source_id


def save_jobs(jobs, source_id):
    saved_count = 0

    with get_connection() as conn:
        with conn.cursor() as cur:

            for job in jobs:

                if not job.get("reference"):
                    continue

                cur.execute("""
                    INSERT INTO jobs (
                        source_id,
                        external_reference,
                        title,
                        company,
                        description,
                        city,
                        postal_code,
                        salary_min,
                        salary_max,
                        pay_unit,
                        contract_type,
                        distance_km,
                        published_at,
                        application_url
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (source_id, external_reference)
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        company = EXCLUDED.company,
                        salary_min = EXCLUDED.salary_min,
                        salary_max = EXCLUDED.salary_max,
                        distance_km = EXCLUDED.distance_km,
                        updated_at = CURRENT_TIMESTAMP;
                """, (
                    source_id,
                    job["reference"],
                    job.get("title"),
                    job.get("company"),
                    job.get("description"),
                    job.get("city"),
                    job.get("postal_code"),
                    job.get("salary_min"),
                    job.get("salary_max"),
                    job.get("pay_unit"),
                    job.get("contract_type"),
                    job.get("distance_km"),
                    job.get("published_at"),
                    job.get("application_url")
                ))

                saved_count += 1

    return saved_count


def get_job_id(source_id, reference):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id
                FROM jobs
                WHERE source_id = %s AND external_reference = %s;
            """, (source_id, reference))

            row = cur.fetchone()

    return row[0] if row is not None else None


def save_analysis(job_id, job, analysis):
    matched_skills = analysis.get("matched_skills", [])
    missing_skills = analysis.get("missing_skills", [])
    required_skills = list(dict.fromkeys([*matched_skills, *missing_skills]))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO job_analyses (
                    job_id,
                    matching_score,
                    matching_coverage,
                    required_skills,
                    matched_skills,
                    missing_skills,
                    ai_relevance,
                    recommendation,
                    ai_analysis,
                    analysis_model
                )
                VALUES (
                    %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb,
                    %s, %s, %s::jsonb, %s
                );
            """, (
                job_id,
                job.get("match_score"),
                job.get("coverage"),
                json.dumps(required_skills),
                json.dumps(matched_skills),
                json.dumps(missing_skills),
                analysis.get("profile_relevance"),
                analysis.get("recommendation"),
                json.dumps(analysis),
                analysis.get("analysis_mode")
            ))