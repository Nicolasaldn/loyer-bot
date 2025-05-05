import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

print("🧪 Démarrage du script de test")

# === Vérification des variables d'environnement ===
try:
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("🔴 TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID manquant")
    if not SHEET_ID or not raw_creds:
        raise ValueError("🔴 GOOGLE_SHEET_ID ou GOOGLE_SHEET_CREDENTIALS_JSON manquant")

    print("✅ Variables d'environnement présentes.")
except Exception as e:
    print("❌ Erreur lecture des variables d'environnement :", e)
    exit(1)

# === Test JSON Credentials ===
try:
    print("🔍 Début du parsing du JSON...")
    credentials = json.loads(raw_creds)
    print("✅ JSON chargé avec succès.")
    print("🔑 Type :", credentials.get("type"))
    print("📧 Email du bot :", credentials.get("client_email"))
except Exception as e:
    print("❌ Erreur parsing JSON :", e)
    exit(1)

# === Connexion Google Sheets ===
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion à Google Sheets réussie.")
except Exception as e:
    print("❌ Échec de connexion à Google Sheets :", e)
    exit(1)

# === Accès à la feuille ===
try:
    sheet = client.open_by_key(SHEET_ID).worksheet("Interface")
    print("✅ Accès à la feuille 'Interface' réussi.")
except Exception as e:
    print("❌ Impossible d’accéder à la feuille 'Interface' :", e)
    exit(1)

# === Lecture des données ===
try:
    rows = sheet.get_all_values()
    print(f"📄 {len(rows)-1} lignes lues (en-tête ignoré).")

    if len(rows) < 2:
        print("⚠️ Feuille vide ou uniquement l'en-tête.")
    else:
        print("🔍 Aperçu 1ère ligne de données :", rows[1])
except Exception as e:
    print("❌ Erreur lecture des lignes :", e)
    exit(1)

# === Envoi rapport test via Telegram ===
msg = f"""✅ Rapport d’intégration :
- Google Sheet OK
- Feuille 'Interface' OK
- {len(rows)-1} ligne(s) lue(s)
"""

try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    r = requests.post(url, data=payload)
    print(f"📤 Message Telegram envoyé : {r.status_code}")
    print(r.text)
except Exception as e:
    print("❌ Erreur envoi Telegram :", e)
