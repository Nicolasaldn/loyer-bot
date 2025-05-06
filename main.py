import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Test ouverture du fichier Google Sheet")

# === Variables ===
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

try:
    creds_dict = json.loads(raw_creds)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Auth OK")

    spreadsheet = client.open_by_key(SHEET_ID)
    print(f"✅ Fichier ouvert avec succès : {spreadsheet.title}")

    worksheets = spreadsheet.worksheets()
    print("🗂️ Onglets disponibles :", [ws.title for ws in worksheets])

except Exception as e:
    print("❌ Erreur :", e)
