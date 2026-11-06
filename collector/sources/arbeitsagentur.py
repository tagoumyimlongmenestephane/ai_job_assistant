
import requests
import json


def rechercher_offres():
    # API endpoint
    url = "https://web.arbeitsagentur.de/portal/portalsuche/"

    # API authentication and identification
    headers = {
        "X-API-Key": "jobboerse-jobsuche"
    }

    # Search parameters
    params = {
        "was": "informatik",
        "wo": "Gießen",
        "umkreis": 25,
        "size": 30,
        "page": 1,
        "veroeffentlichtseit": 7,
        "stichwort": "it-Jobs"
    }

    try:
        # Send the request to the API
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        # Check whether the request succeeded
        response.raise_for_status()

        # Convert the JSON response to a Python dictionary
        donnees = response.json()

        # Retrieve the job listings
        offres = donnees.get("ergebnisliste", [])

        print(f"Nombre d'offres trouvées : {donnees.get('maxErgebnisse', 0)}")
        print("-" * 50)

        for offre in offres:
            titre = offre.get("stellenangebotsTitel", "Titre inconnu")
            entreprise = offre.get("firma", "Entreprise inconnue")
            reference = offre.get("referenznummer", "N/A")

            # Retrieve the first location
            localisations = offre.get("stellenlokationen", [])
            ville = "Ville inconnue"

            if localisations:
                adresse = localisations[0].get("adresse", {})
                ville = adresse.get("ort", "Ville inconnue")

            # Retrieve the salary
            salaire_min = offre.get("gehaltsspanneVon")
            salaire_max = offre.get("gehaltsspanneBis")

            print(f"Poste : {titre}")
            print(f"Entreprise : {entreprise}")
            print(f"Ville : {ville}")

            if salaire_min is not None and salaire_max is not None:
                print(f"Salaire : {salaire_min} - {salaire_max} €/h")
            else:
                print("Salaire : Non indiqué")

            print(f"Référence : {reference}")
            print("-" * 50)

        # Save the raw data
        with open("jobs_test.json", "w", encoding="utf-8") as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=4)

        print("Données sauvegardées dans jobs_test.json")

    except requests.exceptions.RequestException as erreur:
        print(f"Erreur lors de la requête API : {erreur}")

    except ValueError as erreur:
        print(f"Erreur lors de la lecture JSON : {erreur}")


if __name__ == "__main__":
    rechercher_offres()
