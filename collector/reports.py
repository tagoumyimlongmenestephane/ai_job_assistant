
"""Generate reports from the AI Job Assistant database."""
import csv
import json
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font

def generate_global_report(conn):
    """Display general statistics about collected jobs."""

    query = """
        SELECT
            COUNT(DISTINCT j.id) AS total_jobs,
            COUNT(DISTINCT a.job_id) AS analyzed_jobs,
            COUNT(DISTINCT CASE
                WHEN a.matching_score >= 70 THEN j.id
            END) AS interesting_jobs
        FROM jobs j
        LEFT JOIN job_analyses a ON j.id = a.job_id;
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()

    print("\n========== GLOBAL REPORT ==========")
    print(f"Total jobs:       {result[0]}")
    print(f"Analyzed jobs:    {result[1]}")
    print(f"Interesting jobs: {result[2]}")


def generate_top_jobs_report(conn, limit=10):
    """Display the jobs with the highest matching scores."""

    query = """
        SELECT
            j.title,
            j.company,
            j.city,
            a.matching_score,
            a.ai_relevance,
            a.recommendation,
            j.application_url
        FROM jobs j
        INNER JOIN job_analyses a ON j.id = a.job_id
        ORDER BY a.matching_score DESC
        LIMIT %s;
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (limit,))
        jobs = cursor.fetchall()

    print("\n========== TOP JOB OFFERS ==========")

    if not jobs:
        print("No analyzed jobs found.")
        return

    for index, job in enumerate(jobs, start=1):
        print(f"\n{index}. {job[0]}")
        print(f"   Company: {job[1]}")
        print(f"   City: {job[2]}")
        print(f"   Matching score: {job[3]}")
        print(f"   AI relevance: {job[4]}")
        print(f"   Recommendation: {job[5]}")
        print(f"   Application URL: {job[6]}")


def generate_contract_report(conn):
    """Display the number of jobs by contract type."""

    query = """
        SELECT
            COALESCE(contract_type, 'UNKNOWN') AS contract_type,
            COUNT(*) AS total
        FROM jobs
        GROUP BY contract_type
        ORDER BY total DESC;
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    print("\n========== CONTRACT REPORT ==========")

    for contract_type, total in results:
        print(f"{contract_type}: {total}")


def get_export_data(conn):
    """Retrieve jobs and their analysis for export."""

    query = """
        SELECT
            j.title,
            j.company,
            j.city,
            j.postal_code,
            j.salary_min,
            j.salary_max,
            j.pay_unit,
            j.contract_type,
            j.distance_km,
            j.published_at,
            j.application_url,
            a.matching_score,
            a.matching_coverage,
            a.ai_relevance,
            a.recommendation,
            a.required_skills,
            a.matched_skills,
            a.missing_skills,
            a.analysis_model
        FROM jobs j
        LEFT JOIN job_analyses a ON j.id = a.job_id
        ORDER BY a.matching_score DESC NULLS LAST;
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        headers = [column.name for column in cursor.description]

    return headers, rows


def export_jobs_csv(conn):
    """Export jobs and analyses to a CSV file."""

    headers, rows = get_export_data(conn)

    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    file_path = export_dir / "jobs_report.csv"

    with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(headers)

        for row in rows:
            writer.writerow([
                json.dumps(value, ensure_ascii=False, default=str)
                if isinstance(value, (list, dict))
                else value
                for value in row
            ])

    print(f"CSV report generated: {file_path}")


def export_jobs_excel(conn):
    """Export jobs and analyses to an Excel file."""

    headers, rows = get_export_data(conn)

    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    file_path = export_dir / "jobs_report.xlsx"

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Job Offers"

    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for row in rows:
        clean_row = [
            json.dumps(value, ensure_ascii=False, default=str)
            if isinstance(value, (list, dict))
            else value
            for value in row
        ]
        sheet.append(clean_row)

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    for column in sheet.columns:
        column_letter = column[0].column_letter
        max_length = max(
            len(str(cell.value or "")) for cell in column
        )
        sheet.column_dimensions[column_letter].width = min(
            max_length + 2, 45
        )

    workbook.save(file_path)

    print(f"Excel report generated: {file_path}")
