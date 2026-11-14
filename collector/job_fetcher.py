
"""Fetch live job offers from Bundesagentur für Arbeit."""

import requests

BASE_URL = (
    "https://rest.arbeitsagentur.de/"
    "jobboerse/jobsuche-service/pc/v6/jobs"
)

HEADERS = {
    "X-API-Key": "jobboerse-jobsuche",
    "Accept": "application/json",
}


def fetch_jobs(
    keyword="Lagerhelfer",
    location="Gießen",
    radius=25,
    days=7,
    page=1,
    size=100
):
    params = {
        "was": keyword,
        "wo": location,
        "umkreis": radius,
        "veroeffentlichtseit": days,
        "page": page,
        "size": size,
    }

    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def fetch_all_jobs():

    keywords = [
        "Lagerhelfer",
        "Kommissionierer",
        "Reinigungskraft",
        "Putzkraft",
        "Spülkraft",
        "Küchenhilfe",
        "Aushilfe",
        "Werkstudent",
        "Minijob",
        "Produktionshelfer"
    ]

    all_jobs = {}

    for keyword in keywords:

        print(f"\nRecherche : {keyword}")

        try:
            data = fetch_jobs(
                keyword=keyword,
                location="Gießen",
                radius=25,
                days=7,
                page=1,
                size=100
            )

            offers = data.get("ergebnisliste", [])

            print("Offres trouvées :", len(offers))

            for job in offers:
                reference = job.get("referenznummer")

                if reference:
                    all_jobs[reference] = job

        except requests.exceptions.RequestException as error:
            print(f"Erreur pour {keyword} :", error)
            continue

    print(
        "\nTotal après suppression des doublons :",
        len(all_jobs)
    )

    return {"ergebnisliste": list(all_jobs.values())}
