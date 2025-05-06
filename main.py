import os
import json
import gspread
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

print("🧪 Test : visibilité des fichiers Google Drive")

# Variables
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

try:
    creds_dict = json.loads(raw_creds)

    # Création credentials Google API v3
    scopes = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    service = build("drive", "v3", credentials=credentials)

    # Requête : liste les fichiers visibles
    results = service.files().list(
        pageSize=10,
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get("files", [])

    if not files:
        message = "⚠️ Aucun fichier Google Sheet visible par le bot."
    else:
        message = "📂 Fichiers visibles :\n" + "\n".join(f"- {f['name']} ({f['id']})" for f in files)

except Exception as e:
    message = f"❌ Erreur Drive API : {str(e)}"

# Envoi du message Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": message})
