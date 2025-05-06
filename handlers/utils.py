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

# Lecture des données de l’onglet Interface
def get_sheet_data():
    client = get_gsheet_client()
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    return sheet.worksheet("Interface").get_all_records()

# Lecture robuste de l’onglet DB avec gestion des cas tordus
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
