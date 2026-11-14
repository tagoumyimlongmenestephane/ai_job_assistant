def save_jobs(conn, jobs, source_id):

    query = """
        INSERT INTO jobs (
            source_id,
            external_reference,
            title,
            company,
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
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (source_id, external_reference)
        DO UPDATE SET
            title = EXCLUDED.title,
            company = EXCLUDED.company,
            salary_min = EXCLUDED.salary_min,
            salary_max = EXCLUDED.salary_max,
            distance_km = EXCLUDED.distance_km,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id;
    """

    saved_ids = []

    with conn.cursor() as cursor:
        for job in jobs:

            contract_type = None

            if job.get("is_minijob"):
                contract_type = "MINIJOB"
            elif job.get("is_part_time"):
                contract_type = "TEILZEIT"
            elif job.get("is_full_time"):
                contract_type = "VOLLZEIT"

            values = (
                source_id,
                job.get("reference"),
                job.get("title"),
                job.get("company"),
                job.get("city"),
                job.get("postal_code"),
                job.get("salary_min"),
                job.get("salary_max"),
                job.get("pay_unit"),
                contract_type,
                job.get("distance_km"),
                job.get("published_at"),
                job.get("application_url")
            )

            if not job.get("reference") or not job.get("title"):
                continue

            cursor.execute(query, values)
            result = cursor.fetchone()

            saved_ids.append(result[0])

    conn.commit()

    return saved_ids