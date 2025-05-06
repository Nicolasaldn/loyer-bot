import re
import unicodedata
from datetime import datetime, timedelta
from utils.sheets import list_tenants

FRENCH_MONTHS = {
    "janvier": 1,
    "fevrier": 2, "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8, "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12, "décembre": 12
}

def normalize(text):
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8").lower()

def extract_name_and_date(message: str):
    tenants = list_tenants()
    msg_lower = normalize(message)

    found_name = next((name for name in tenants if normalize(name) in msg_lower), None)

    date_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", message)
    if date_match:
        try:
            datetime.strptime(date_match.group(1), "%d/%m/%Y")
            return found_name, date_match.group(1)
        except ValueError:
            pass

    return found_name, None

def parse_quittance_period(text: str):
    msg = normalize(text).strip()

    pattern_simple = re.search(r"\b(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+(\d{4})", msg)
    pattern_range = re.search(
        r"de\s+(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+(\d{4})\s+"
        r"a\s+(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+(\d{4})",
        msg
    )

    try:
        if pattern_range:
            mois_debut = FRENCH_MONTHS.get(pattern_range.group(1))
            annee_debut = int(pattern_range.group(2))
            mois_fin = FRENCH_MONTHS.get(pattern_range.group(3))
            annee_fin = int(pattern_range.group(4))

            date_debut = datetime(annee_debut, mois_debut, 1)
            next_month = datetime(annee_fin, mois_fin, 28) + timedelta(days=4)
            date_fin = (next_month - timedelta(days=next_month.day))
            return date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y")

        elif pattern_simple:
            mois = FRENCH_MONTHS.get(pattern_simple.group(1))
            annee = int(pattern_simple.group(2))
            date_debut = datetime(annee, mois, 1)
            next_month = datetime(annee, mois, 28) + timedelta(days=4)
            date_fin = (next_month - timedelta(days=next_month.day))
            return date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y")

    except Exception:
        pass

    return None, None
