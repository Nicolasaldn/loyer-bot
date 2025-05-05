import os
import json
import gspread
import requests
import sys
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Début du script de test")

# Lecture des variables d'environnement
try:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    CREDENTIALS_JSON = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

    print("📦 Variables d'environnement chargées.")
    print(f"🔍 Token tronqué : {TELEGRAM_TOKEN[:6]}... | Sheet ID : {GOOGLE_SHEET_ID[:6]}...")
except Exception as e:
    print("❌ Erreur lecture variables :", e)
    sys.exit(1)

# Chargement du JSON
try:
    print("🔍 Contenu brut détecté (début) :", CREDENTIALS_JSON[:50].replace('\n', ''))
    credentials = json.loads(CREDENTIALS_JSON)
    print("✅ JSON chargé avec succès.")
except Exception as e:
    print("❌ Erreur chargement JSON :", e)
    sys.exit(1)

# Connexion Google Sheets
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("Interface")
    print("✅ Connexion à Google Sheet réussie.")
except Exception as e:
    print("❌ Erreur connexion Google Sheets :", e)
    sys.exit(1)

# Lecture des données
try:
    rows = sheet.get_all_values()[1:]
    print(f"📄 {len(rows)} lignes détectées dans la feuille.")
except Exception as e:
    print("❌ Erreur lecture données Google Sheet :", e)
    sys.exit(1)

# Analyse
messages = []
for i, row in enumerate(rows):
    try:
        nom = row[0] if len(row) > 0 else ""
        adresse = row[2] if len(row) > 2 else ""
        loyer = row[3] if len(row) > 3 else ""
        proprio = row[6] if len(row) > 6 else ""
        rappel = row[7].strip().lower() if len(row) > 7 else ""

        print(f"🔎 L{i+2} : {nom} | {adresse} | {loyer}€ | {proprio} | Rappel : {rappel}")

        if rappel in ["x", "✓", "true", "oui"]:
            messages.append(f"🔔 {nom} – {adresse} – {loyer}€ – Propriétaire : {proprio}")
    except Exception as e:
        print(f"⚠️ Erreur ligne {i+2} :", e)

# Envoi Telegram
try:
    if messages:
        message = "📅 Rappels à envoyer :\n" + "\n".join(messages)
    else:
        message = "✅ Aucun rappel aujourd'hui."

    print("✉️ Message Telegram :\n", message)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    response = requests.post(url, data=payload)
    print("📤 Statut Telegram :", response.status_code, response.text)
except Exception as e:
    print("❌ Erreur envoi Telegram :", e)
    sys.exit(1)

# === Fin propre ===
print("✅ Script terminé avec succès.")
sys.exit(0)
