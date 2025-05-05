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

# Lecture des données
rows = sheet.get_all_values()[1:]  # ignore l'en-tête

messages = []

for row in rows:
    try:
        nom = row[0]
        adresse = row[2]
        loyer = row[3]
        proprio = row[6]
        rappel = row[7].strip().lower()

        if rappel in ["x", "✓", "true", "oui"]:
            messages.append(f"🔔 {nom} – {adresse} – {loyer} EUR – Propriétaire : {proprio}")
    except IndexError:
        continue

# Envoi du message Telegram
if messages:
    message = "📅 Locataires à relancer :\n" + "\n".join(messages)
else:
    message = "✅ Aucun rappel de loyer à envoyer aujourd’hui."

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, data=payload)
print("Message envoyé:", response.status_code, response.text)
