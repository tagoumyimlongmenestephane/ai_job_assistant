def clean_text(value):
    """Clean a text value."""
    if not isinstance(value, str):
        return None

    value = " ".join(value.split())

    return value if value else None


def to_number(value):
    """Convert a value to a number."""
    try:
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def extract_location(job):
    """Extract the city and postal code."""

    locations = job.get("stellenlokationen")

    if not locations:
        return {
            "city": None,
            "postal_code": None
        }

    address = locations[0].get("adresse") or {}

    return {
        "city": clean_text(address.get("ort")),
        "postal_code": clean_text(address.get("plz"))
    }


def extract_salary(job):
    """Extract salary information."""

    return {
        "salary_min": to_number(job.get("gehaltsspanneVon")),
        "salary_max": to_number(job.get("gehaltsspanneBis")),
        "fixed_salary": to_number(job.get("festgehalt")),
        "pay_unit": job.get("verguetungsangabe")
    }


def extract_contract(job):
    """Identify working-hours information."""

    part_time_fields = [
        "arbeitszeitTeilzeitAbend",
        "arbeitszeitTeilzeitNachmittag",
        "arbeitszeitTeilzeitVormittag",
        "arbeitszeitTeilzeitFlexibel"
    ]

    is_part_time = any(
        job.get(field) is True
        for field in part_time_fields
    )

    return {
        "is_minijob": job.get("istGeringfuegigeBeschaeftigung"),
        "is_full_time": job.get("arbeitszeitVollzeit"),
        "is_part_time": True if is_part_time else None
    }


def normalize_job(job):
    """Transform a raw job listing into a standardized listing."""

    location = extract_location(job)
    salary = extract_salary(job)
    contract = extract_contract(job)

    return {
        "reference": clean_text(job.get("referenznummer")),
        "title": clean_text(job.get("stellenangebotsTitel")),
        "company": clean_text(job.get("firma")),
        "description": clean_text(job.get("stellenbeschreibung")),
        **location,
        **salary,
        **contract,

        "distance_km": to_number(job.get("entfernung")),
        "published_at": job.get("datumErsteVeroeffentlichung"),
        "application_url": job.get("externeURL")
    }


def remove_duplicates(jobs):
    """Remove job listings with duplicate references."""

    unique_jobs = {}

    for job in jobs:
        reference = job.get("reference")

        if not reference:
            continue

        unique_jobs[reference] = job

    return list(unique_jobs.values())


def normalize_jobs(jobs):
    """Normalize a list of job listings."""

    normalized = [
        normalize_job(job)
        for job in jobs['ergebnisliste']
    ]
    return remove_duplicates(normalized)
