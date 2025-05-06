import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
TAB_INTERFACE = "Interface"
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
