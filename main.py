import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Lecture des variables d'environnement
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON"))

# Connexion Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet("Interface")  # Feuille 'Interface'

print("✅ Connexion Google Sheets réussie.")

# Lecture des données
rows = sheet.get_all_values()[1:]  # ignore l'en-tête
print(f"📋 {len(rows)} lignes trouvées dans la feuille 'Interface'.")

messages = []

for i, row in enumerate(rows):
    try:
        nom = row[0]
        adresse = row[2]
        loyer = row[3]
        proprio = row[6]
        rappel = row[7].strip().lower()

        print(f"🔎 Ligne {i+2}: {nom} | {adresse} | {loyer} | {proprio} | Rappel={rappel}")

        if rappel in ["x", "✓", "true", "oui"]:
            messages.append(f"🔔 {nom} – {adresse} – {loyer} EUR – Propriétaire : {proprio}")
    except IndexError:
        print(f"⚠️ Ligne {i+2} ignorée (IndexError)")

# Envoi du message Telegram
if messages:
    message = "📅 Locataires à relancer :\n" + "\n".join(messages)
else:
    message = "✅ Aucun rappel de loyer à envoyer aujourd’hui."

print("📨 Message à envoyer via Telegram :\n" + message)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, data=payload)
print("📤 Statut de l'envoi Telegram :", response.status_code, response.text)
