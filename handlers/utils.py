import os
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Connexion Google Sheets via Service Account
def get_gsheet_client():
    creds_dict = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON"))
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Lecture des données de l’onglet Interface (headers en ligne 5)
def get_sheet_data():
    client = get_gsheet_client()
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    interface = sheet.worksheet("Interface").get_all_records(head=5)  # 👈 Correction ici
    return interface

# Dictionnaire des propriétaires depuis l’onglet DB
def get_db_dict():
    client = get_gsheet_client()
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    db = sheet.worksheet("DB").get_all_records()
    return {row["Nom"]: row["Adresse"] for row in db if row["Nom"]}

# Tentative de conversion string en date
def parse_date_from_text(text):
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]:
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
    return None

# Analyse de la commande utilisateur
def parse_command(text):
    text = text.strip()
    if text.lower().startswith("rappel "):
        parts = text.split(" ", 2)
        if len(parts) == 3:
            date = parse_date_from_text(parts[2])
            if parts[1].lower() in ["tous", "all"]:
                return {
                    "source": "rappel",
                    "type": "all",
                    "date": date
                }
            else:
                return {
                    "source": "rappel",
                    "type": "single",
                    "nom": parts[1],
                    "date": date
                }
    elif text.lower().startswith("quittance "):
        return {
            "source": "quittance",
            "nom": text[9:].strip()
        }
    return None
