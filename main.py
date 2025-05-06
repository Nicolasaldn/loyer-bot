import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Lancement script complet - Lecture + Message Telegram")

# === Variables d'environnement ===
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SHEET_NAME = "RE - Gestion"
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

# === Authentification Google Sheets ===
try:
    creds_dict = json.loads(raw_creds)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Authentification réussie")
except Exception as e:
    print("❌ Erreur d'authentification :", e)
    exit(1)

# === Accès à la feuille Interface ===
try:
    spreadsheet = client.open(SHEET_NAME)
    print(f"✅ Fichier ouvert : {spreadsheet.title}")

    worksheets = spreadsheet.worksheets()
    print("🗂️ Onglets disponibles :", [ws.title for ws in worksheets])

    sheet = spreadsheet.worksheet("Interface")
    rows = sheet.get_all_values()
    nb_rows = len(rows) - 1  # ignore l'en-tête

    if nb_rows <= 0:
        message = "⚠️ Feuille 'Interface' vide ou en-tête seul."
    else:
        aperçu = ", ".join(rows[1][:4])  # 4 premières colonnes de la première ligne de données
        message = f"✅ Lecture réussie : {nb_rows} ligne(s) trouvée(s).\n👁️ Aperçu ligne 1 : {aperçu}"

except Exception as e:
    message = f"❌ Erreur lors de l'accès à la feuille 'Interface' :\n{str(e)}"
    print(message)

# === Envoi Telegram ===
try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    print(f"📤 Message Telegram envoyé : {response.status_code}")
except Exception as e:
    print("❌ Erreur d’envoi Telegram :", e)
