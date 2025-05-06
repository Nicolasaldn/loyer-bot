# utils/parser.py

import re
from datetime import datetime
from utils.sheets import list_tenants

def extract_name_and_date(message: str):
    tenants = list_tenants()
    msg_lower = message.lower()

    # --- Trouver un nom de locataire dans le message
    found_name = next((name for name in tenants if name.lower() in msg_lower), None)

    # --- Chercher une date au format JJ/MM/AAAA
    date_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", message)
    if date_match:
        try:
            date_obj = datetime.strptime(date_match.group(1), "%d/%m/%Y")
            formatted_date = date_obj.strftime("%B %Y")  # ex: January 2025
            return found_name, formatted_date
        except ValueError:
            pass

    return found_name, None
