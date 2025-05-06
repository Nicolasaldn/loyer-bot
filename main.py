import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Script de test lecture de l’onglet Interface")

# === Variables d'environnement ===
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

# === Authentification Google Sheets ===
try:
    creds_dict = json.loads(raw_creds)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion Google Sheets OK")
except Exception as e:
    print("❌ Erreur d'authentification :", e)
    exit(1)

# === Accès à la feuille Interface ===
try:
    sheet = client.open_by_key(SHEET_ID).worksheet("Interface")
    rows = sheet.get_all_values()
    nb_rows = len(rows) - 1  # En-tête ignoré

    if nb_rows <= 0:
        message = "⚠️ Feuille 'Interface' vide ou en-tête seul."
    else:
        aperçu = ", ".join(rows[1][:4])  # Affiche 4 premières colonnes de la 1re ligne
        message = f"✅ Lecture réussie : {nb_rows} ligne(s) trouvée(s).\n👁️ Aperçu ligne 1 : {aperçu}"

except Exception as e:
    message = f"❌ Erreur lors de l'accès à la feuille 'Interface' :\n{str(e)}"
    print(message)

# === Envoi Telegram ===
try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    print(f"📤 Telegram envoyé : {response.status_code}")
except Exception as e:
    print("❌ Erreur d’envoi Telegram :", e)
