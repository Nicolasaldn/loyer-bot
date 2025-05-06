# utils/parser.py

import re
from datetime import datetime
from utils.sheets import list_tenants

FRENCH_MONTHS = {
    "janvier": 1,
    "février": 2, "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8, "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12, "decembre": 12
}

def extract_name_and_date(message: str):
    tenants = list_tenants()
    msg_lower = message.lower()

    # --- Trouver un nom de locataire dans le message
    found_name = next((name for name in tenants if name.lower() in msg_lower), None)

    # --- Chercher une date au format JJ/MM/AAAA
    date_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", message)
    if date_match:
        try:
            datetime.strptime(date_match.group(1), "%d/%m/%Y")
            return found_name, date_match.group(1)
        except ValueError:
            pass

    return found_name, None

def parse_quittance_period(text: str):
    msg = text.lower().strip()
    pattern_simple = re.search(r"(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})", msg)
    pattern_range = re.search(
        r"de\s+(\w+)\s+(\d{4})\s+à\s+(\w+)\s+(\d{4})",
        msg
    )

    try:
        if pattern_range:
            mois_debut = FRENCH_MONTHS.get(pattern_range.group(1))
            annee_debut = int(pattern_range.group(2))
            mois_fin = FRENCH_MONTHS.get(pattern_range.group(3))
            annee_fin = int(pattern_range.group(4))

            date_debut = datetime(annee_debut, mois_debut, 1)
            # Fin = dernier jour du mois
            next_month = datetime(annee_fin, mois_fin, 28) + timedelta(days=4)
            date_fin = datetime(annee_fin, mois_fin, (next_month - timedelta(days=next_month.day)).day)
            return date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y")

        elif pattern_simple:
            mois = FRENCH_MONTHS.get(pattern_simple.group(1))
            annee = int(pattern_simple.group(2))
            date_debut = datetime(annee, mois, 1)
            next_month = datetime(annee, mois, 28) + timedelta(days=4)
            date_fin = datetime(annee, mois, (next_month - timedelta(days=next_month.day)).day)
            return date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y")

    except Exception:
        pass

    return None, None
