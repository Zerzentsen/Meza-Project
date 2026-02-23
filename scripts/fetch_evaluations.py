"""
Nom du script : fetch_evaluations.py
Description   : Recupere les donnees d'evaluations depuis l'API LearnyBox
                et les exporte en CSV.
Auteur        : Meza-Project
Date          : 2026-02-23

Dependances :
    - requests (pip install requests)
    - python-dotenv (pip install python-dotenv)

Usage :
    python scripts/fetch_evaluations.py --user-id 123
    python scripts/fetch_evaluations.py --user-id 123 --evaluation-id 456
    python scripts/fetch_evaluations.py --user-id 123 --output resultats.csv

Parametres :
    --user-id          ID de l'utilisateur LearnyBox (obligatoire)
    --evaluation-id    ID d'une evaluation specifique (optionnel)
    --output           Chemin du fichier CSV de sortie (defaut: evaluations.csv)
    --verbose          Active les logs detailles

Exemple :
    python scripts/fetch_evaluations.py --user-id 42 --output mes_evaluations.csv
"""

import argparse
import csv
import json
import logging
import os
import sys

# Ajouter le repertoire racine au path pour importer libs/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

from libs.learnybox_client import LearnyBoxAPIError, LearnyBoxClient

logger = logging.getLogger(__name__)


def flatten_dict(d, parent_key="", sep="_"):
    """Aplatit un dictionnaire imbrique pour l'export CSV."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v, ensure_ascii=False)))
        else:
            items.append((new_key, v))
    return dict(items)


def write_csv(rows, output_path):
    """Ecrit une liste de dictionnaires en CSV."""
    if not rows:
        print(f"Aucune donnee a exporter.")
        return

    # Aplatir les structures imbriquees
    flat_rows = [flatten_dict(row) if isinstance(row, dict) else {"value": row} for row in rows]

    # Collecter toutes les cles pour les colonnes
    all_keys = []
    for row in flat_rows:
        for key in row:
            if key not in all_keys:
                all_keys.append(key)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore", delimiter=";")
        writer.writeheader()
        writer.writerows(flat_rows)

    print(f"Export CSV : {len(flat_rows)} ligne(s) -> {output_path}")


def fetch_user_evaluations(client, user_id):
    """Recupere la liste des evaluations d'un utilisateur."""
    print(f"Recuperation des evaluations pour l'utilisateur {user_id}...")
    result = client.get_user_evaluations(user_id)
    data = result.get("data", result)
    if isinstance(data, dict) and not any(k.isdigit() for k in data.keys()):
        data = [data]
    elif isinstance(data, dict):
        data = list(data.values())
    return data


def fetch_evaluation_responses(client, evaluation_id, user_id):
    """Recupere les reponses a une evaluation specifique pour un utilisateur."""
    print(f"Recuperation des reponses a l'evaluation {evaluation_id} pour l'utilisateur {user_id}...")
    result = client.get_evaluation_responses(evaluation_id, user_id)
    data = result.get("data", result)
    if isinstance(data, dict) and not any(k.isdigit() for k in data.keys()):
        data = [data]
    elif isinstance(data, dict):
        data = list(data.values())
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Recupere les evaluations LearnyBox et les exporte en CSV."
    )
    parser.add_argument(
        "--user-id",
        required=True,
        help="ID de l'utilisateur LearnyBox.",
    )
    parser.add_argument(
        "--evaluation-id",
        default=None,
        help="ID d'une evaluation specifique (optionnel). "
        "Si omis, liste toutes les evaluations de l'utilisateur.",
    )
    parser.add_argument(
        "--output",
        default="evaluations.csv",
        help="Chemin du fichier CSV de sortie (defaut: evaluations.csv).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Active les logs detailles.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Charger la configuration depuis .env
    load_dotenv()
    api_key = os.getenv("LEARNYBOX_API_KEY")
    subdomain = os.getenv("LEARNYBOX_SUBDOMAIN", "mezaelle-hkc")

    if not api_key:
        print("ERREUR: Variable d'environnement LEARNYBOX_API_KEY non definie.")
        print("Creez un fichier .env avec :")
        print("  LEARNYBOX_API_KEY=votre_cle_api")
        print("  LEARNYBOX_SUBDOMAIN=mezaelle-hkc")
        sys.exit(1)

    # Initialiser le client et s'authentifier
    client = LearnyBoxClient(api_key=api_key, subdomain=subdomain)

    try:
        client.authenticate()
    except LearnyBoxAPIError as e:
        print(f"ERREUR d'authentification: {e}")
        sys.exit(1)

    try:
        if args.evaluation_id:
            # Recuperer les reponses a une evaluation specifique
            data = fetch_evaluation_responses(client, args.evaluation_id, args.user_id)
        else:
            # Recuperer toutes les evaluations de l'utilisateur
            data = fetch_user_evaluations(client, args.user_id)

        # Afficher un apercu des donnees brutes
        if args.verbose:
            print(f"\nDonnees brutes ({len(data)} elements) :")
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str))

        # Exporter en CSV
        write_csv(data, args.output)

    except LearnyBoxAPIError as e:
        print(f"ERREUR API: {e}")
        sys.exit(1)
    finally:
        client.revoke_token()


if __name__ == "__main__":
    main()
