import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Test complet d’accès Google Sheet")

# Récupération des variables d’environnement
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

# Étape 1 : Authentification
try:
    creds_dict = json.loads(raw_creds)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion Google API OK")
except Exception as e:
    print("❌ Authentification Google Sheets échouée :", e)
    exit(1)

# Étape 2 : Ouverture du fichier et récupération des onglets
try:
    spreadsheet = client.open_by_key(SHEET_ID)
    file_title = spreadsheet.title
    worksheets = spreadsheet.worksheets()
    sheet_names = [ws.title for ws in worksheets]

    print(f"📄 Fichier : {file_title}")
    print("🗂️ Onglets trouvés :", sheet_names)

    # Message à envoyer par Telegram
    if "Interface" in sheet_names:
        message = f"✅ Le fichier *{file_title}* est accessible.\n✅ L’onglet `Interface` existe bien.\n\n🗂️ Autres onglets trouvés :\n" + "\n".join(f"- {name}" for name in sheet_names)
    else:
        message = f"⚠️ Le fichier *{file_title}* est accessible, mais l’onglet `Interface` est introuvable.\n\n🗂️ Onglets visibles pour le bot :\n" + "\n".join(f"- {name}" for name in sheet_names)

except Exception as e:
    message = f"❌ Erreur accès fichier Google Sheet :\n{str(e)}"
    print(message)

# Étape 3 : Envoi via Telegram
try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, data=payload)
    print(f"📤 Telegram envoyé : {response.status_code}")
except Exception as e:
    print("❌ Échec envoi Telegram :", e)
