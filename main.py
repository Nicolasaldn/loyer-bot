import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

print("🔁 Démarrage du bot...")

# === Lecture des variables d'environnement ===
try:
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    CREDENTIALS = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON"))

    assert BOT_TOKEN and CHAT_ID and SHEET_ID and CREDENTIALS
    print("✅ Variables d'environnement OK.")
except Exception as e:
    print("❌ Erreur dans les variables d'environnement :", e)
    raise

# === Connexion à Google Sheets ===
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet("Interface")
    print("✅ Connexion Google Sheets réussie.")
except Exception as e:
    print("❌ Erreur Google Sheets :", e)
    raise

# === Lecture des données ===
try:
    rows = sheet.get_all_values()[1:]  # ignore l'en-tête
    print(f"📋 {len(rows)} lignes lues dans 'Interface'.")
except Exception as e:
    print("❌ Erreur lecture lignes :", e)
    raise

# === Analyse des lignes ===
messages = []

for i, row in enumerate(rows):
    try:
        nom = row[0] if len(row) > 0 else ""
        adresse = row[2] if len(row) > 2 else ""
        loyer = row[3] if len(row) > 3 else ""
        proprio = row[6] if len(row) > 6 else ""
        rappel = row[7].strip().lower() if len(row) > 7 else ""

        print(f"🔎 Ligne {i+2} : nom={nom}, adresse={adresse}, loyer={loyer}, proprio={proprio}, rappel={repr(rappel)}")

        if rappel in ["x", "✓", "true", "oui"]:
            msg = f"🔔 {nom} – {adresse} – {loyer} EUR – Propriétaire : {proprio}"
            messages.append(msg)
            print("✅ Ajouté :", msg)
        else:
            print("⏭️ Ignoré (rappel non valide)")
    except Exception as e:
        print(f"⚠️ Erreur ligne {i+2} :", e)

# === Envoi du message Telegram ===
try:
    if messages:
        message = "📅 Locataires à relancer :\n" + "\n".join(messages)
    else:
        message = "✅ Aucun rappel de loyer à envoyer aujourd’hui."

    print("📨 Message à envoyer :\n" + message)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=payload)
    print("📤 Envoi Telegram :", response.status_code, response.text)
except Exception as e:
    print("❌ Erreur envoi Telegram :", e)
