import os
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import re

# Connexion Google Sheets via Service Account
def get_gsheet_client():
    creds_dict = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON"))
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

def get_sheet_data():
    client = get_gsheet_client()
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    return sheet.worksheet("Interface").get_all_records()

def get_db_dict():
    client = get_gsheet_client()
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    db_values = sheet.worksheet("DB").get_all_values()

    if not db_values or len(db_values) < 2:
        return {}

    headers = [h.strip() for h in db_values[0]]
    try:
        nom_index = headers.index("Nom")
        adresse_index = headers.index("Adresse")
    except ValueError:
        raise ValueError("⚠️ L’un des en-têtes 'Nom' ou 'Adresse' est manquant ou mal écrit dans la feuille DB.")

    db_dict = {}
    for row in db_values[1:]:
        if len(row) > max(nom_index, adresse_index):
            nom = row[nom_index].strip()
            adresse = row[adresse_index].strip()
            if nom:
                db_dict[nom] = adresse
    return db_dict

def parse_date_from_text(text):
    text = text.strip()
    text = re.sub(r"[^\d/.\-]", "", text)  # nettoie tous les caractères parasites
    print(f"[DEBUG] ➤ Texte date nettoyé : {text}")

    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]:
        try:
            parsed = datetime.strptime(text, fmt)
            print(f"[DEBUG] ➤ Date reconnue avec format {fmt}: {parsed}")
            return parsed
        except ValueError:
            continue
    print("[DEBUG] ❌ Aucun format de date reconnu")
    return None

def parse_command(text):
    text = text.strip()
    print(f"[DEBUG] ➤ Commande brute : {text}")
    
    if text.lower().startswith("rappel "):
        body = text[7:].strip()
        parts = body.rsplit(" ", 1)
        if len(parts) == 2:
            nom = parts[0].strip()
            date = parse_date_from_text(parts[1])
            print(f"[DEBUG] ➤ Nom: {nom}, Date: {date}")
            if nom.lower() in ["tous", "all"]:
                return {
                    "source": "rappel",
                    "type": "all",
                    "date": date
                }
            else:
                return {
                    "source": "rappel",
                    "type": "single",
                    "nom": nom,
                    "date": date
                }

    elif text.lower().startswith("quittance "):
        return {
            "source": "quittance",
            "nom": text[9:].strip()
        }

    print("[DEBUG] ❌ Commande non reconnue")
    return None
