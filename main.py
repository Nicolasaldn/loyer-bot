import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Test Auth Google Sheets")

try:
    raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")
    print("🔍 JSON trouvé ?", raw_creds is not None)

    creds_dict = json.loads(raw_creds)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Authentification réussie.")
except Exception as e:
    print("❌ Erreur d’authentification :", e)
