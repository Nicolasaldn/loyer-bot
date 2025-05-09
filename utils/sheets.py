import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
TAB_INTERFACE = "Interface"
TAB_DB = "DB"
GOOGLE_SHEET_CREDENTIALS = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON"))

def get_worksheet(tab_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEET_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.worksheet(tab_name)

def list_tenants():
    interface = get_worksheet(TAB_INTERFACE)
    values = interface.get_all_values()
    header = values[0]
    name_idx = next((i for i, h in enumerate(header) if "nom" in h.lower()), None)
    if name_idx is None:
        raise ValueError("Colonne des noms introuvable")
    return [row[name_idx] for row in values[1:] if row[name_idx]]

def get_locataire_info(nom_locataire: str) -> dict:
    interface = get_worksheet(TAB_INTERFACE)
    db = get_worksheet(TAB_DB)

    rows_interface = interface.get_all_records()
    rows_db = db.get_all_records()

    loc_data = next((r for r in rows_interface if r["Nom"].strip().lower() == nom_locataire.strip().lower()), None)
    if not loc_data:
        raise ValueError(f"Locataire {nom_locataire} introuvable dans la feuille Interface.")

    nom_bailleur = loc_data.get("Propriétaire") or loc_data.get("Proprietaire")
    bail_data = next((r for r in rows_db if r["Nom du proprietaire"].strip().lower() == nom_bailleur.strip().lower()), None)
    if not bail_data:
        raise ValueError(f"Bailleur {nom_bailleur} introuvable dans la feuille DB.")

    return {
        "locataire_nom": loc_data["Nom"],
        "locataire_adresse": loc_data["Adresse"],
        "locataire_email": loc_data["Email"],
        "bailleur_nom": nom_bailleur,
        "bailleur_adresse": bail_data["Adresse"],
        "loyer_ttc": float(loc_data["Loyer TTC (€)"]),
        "frequence": loc_data["Fréquence"].lower()
    }

def add_tenant(nom, email, adresse, loyer, frequence, proprietaire):
    interface = get_worksheet(TAB_INTERFACE)
    rows = interface.get_all_records()

    if any(row["Nom"].strip().lower() == nom.strip().lower() for row in rows):
        raise ValueError("Locataire déjà existant.")

    interface.append_row([nom, email, adresse, loyer, frequence, proprietaire])


def add_landlord(nom, adresse):
    db = get_worksheet(TAB_DB)
    rows = db.get_all_records()

    if any(row["Nom du proprietaire"].strip().lower() == nom.strip().lower() for row in rows):
        raise ValueError("Bailleur déjà existant.")

    db.append_row([nom, adresse])
