
CRITERIA = {
    "max_distance": 25,
    "min_salary": 15
}

WEIGHTS = {
    "distance": 30,
    "salary": 30,
    "part_time": 20,
    "schedule": 10,
    "transport": 10
}


def calculate_distance_score(job):
    distance = job.get("distance_km")

    if distance is None:
        return None

    if distance <= 10:
        return 30
    elif distance <= 15:
        return 25
    elif distance <= CRITERIA["max_distance"]:
        return 20

    return 0


def calculate_salary_score(job):
    minimum = job.get("salary_min")
    maximum = job.get("salary_max")
    threshold = CRITERIA["min_salary"]

    if minimum is not None and maximum is not None:

        if minimum >= threshold:
            return 30

        if maximum < threshold:
            return 0

        return round(
            30 * (maximum - threshold) / (maximum - minimum),
            2
        )

    fixed = job.get("fixed_salary")

    if fixed is not None and job.get("pay_unit") == "STUNDENLOHN":
        return 30 if fixed >= threshold else 0

    return None


def calculate_part_time_score(job):
    is_part_time = job.get("is_part_time")

    if is_part_time is True:
        return 20

    if is_part_time is False:
        return 0

    return None


def calculate_schedule_score(job):
    # To be implemented using the candidate's schedule.
    return None


def calculate_transport_score(job):
    # To be implemented using public transit data.
    return None


def calculate_match_score(scores):
    earned = 0
    evaluated_weight = 0

    for criterion, score in scores.items():

        if score is None:
            continue

        weight = WEIGHTS[criterion]

        earned += score
        evaluated_weight += weight

    if evaluated_weight == 0:
        return None, 0

    score = round(
        (earned / evaluated_weight) * 100,
        2
    )

    coverage = round(
        (evaluated_weight / sum(WEIGHTS.values())) * 100,
        2
    )

    return score, coverage


def classify_job(score, coverage):

    if score is None:
        return "DONNEES_INSUFFISANTES"

    if coverage < 50:
        return "A_ANALYSER"

    if score >= 80:
        return "TRES_INTERESSANT"

    elif score >= 60:
        return "INTERESSANT"

    elif score >= 40:
        return "MOYEN"

    return "PEU_INTERESSANT"


def match_job(job):

    scores = {
        "distance": calculate_distance_score(job),
        "salary": calculate_salary_score(job),
        "part_time": calculate_part_time_score(job),
        "schedule": calculate_schedule_score(job),
        "transport": calculate_transport_score(job)
    }

    score, coverage = calculate_match_score(scores)

    return {
        "reference": job.get("reference"),
        "title": job.get("title"),
        "company": job.get("company"),
        "city": job.get("city"),
        "distance_km": job.get("distance_km"),
        "scores": scores,
        "match_score": score,
        "coverage": coverage,
        "classification": classify_job(score, coverage)
    }


def match_jobs(jobs):

    results = [
        match_job(job)
        for job in jobs
    ]

    return sorted(
        results,
        key=lambda job: (
            job["match_score"]
            if job["match_score"] is not None
            else -1
        ),
        reverse=True
    )




