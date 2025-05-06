import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Test ouverture Google Sheet avec logs détaillés")

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

try:
    print("🔐 Lecture JSON…")
    creds_dict = json.loads(raw_creds)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Authentification réussie")

    print(f"📄 Tentative d’ouverture du fichier ID = {SHEET_ID}")
    spreadsheet = client.open_by_key(SHEET_ID)
    print(f"✅ Fichier ouvert : {spreadsheet.title}")

    worksheets = spreadsheet.worksheets()
    print("🗂️ Onglets disponibles :", [ws.title for ws in worksheets])

except Exception as e:
    print(f"❌ Exception capturée : {repr(e)}")
