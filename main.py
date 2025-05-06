import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Test ouverture du fichier par nom")

# === Variables ===
SHEET_NAME = "RE - Gestion"
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

try:
    creds_dict = json.loads(raw_creds)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Auth OK")

    spreadsheet = client.open(SHEET_NAME)  # Ouvre le fichier par son nom, plus robuste ici
    print(f"✅ Fichier ouvert : {spreadsheet.title}")

    worksheets = spreadsheet.worksheets()
    print("🗂️ Onglets disponibles :", [ws.title for ws in worksheets])

    sheet = spreadsheet.worksheet("Interface")
    print("✅ Onglet 'Interface' accessible")

except Exception as e:
    print(f"❌ Erreur capturée : {repr(e)}")
