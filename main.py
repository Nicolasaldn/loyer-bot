import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Début du script ultra-verbeux")

# === Chargement des variables d'environnement ===
try:
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    raw_json = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

    print("🔍 Variables récupérées :")
    print(f"  - TELEGRAM_TOKEN présent : {'Oui' if BOT_TOKEN else 'Non'}")
    print(f"  - TELEGRAM_CHAT_ID : {CHAT_ID}")
    print(f"  - GOOGLE_SHEET_ID : {SHEET_ID}")
    print(f"  - JSON (début brut) : {raw_json[:40]}...")

    CREDENTIALS = json.loads(raw_json)
    print("✅ JSON chargé avec succès.")
except Exception as e:
    print("❌ ERREUR au chargement des variables :", e)
    raise

# === Connexion Google Sheets ===
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion Google Sheets réussie.")
except Exception as e:
    print("❌ ERREUR Connexion Google Sheets :", e)
    raise

# === Ouverture de la feuille 'Interface' ===
try:
    sheet = client.open_by_key(SHEET_ID).worksheet("Interface")
    print("✅ Feuille 'Interface' ouverte.")
except Exception as e:
    print("❌ ERREUR ouverture de l’onglet 'Interface' :", e)
    raise

# === Lecture des lignes ===
try:
    rows = sheet.get_all_values()[1:]
    print(f"📋 {len(rows)} lignes lues dans la feuille.")
except Exception as e:
    print("❌ ERREUR lecture des lignes :", e)
    raise

# === Traitement des lignes ===
messages = []
for i, row in enumerate(rows):
    try:
        nom = row[0] if len(row) > 0 else ""
        adresse = row[2] if len(row) > 2 else ""
        loyer = row[3] if len(row) > 3 else ""
        proprio = row[6] if len(row) > 6 else ""
        rappel = row[7].strip().lower() if len(row) > 7 else ""

        print(f"🔎 Ligne {i+2} : {nom} | {adresse} | {loyer} | {proprio} | Rappel={rappel}")

        if rappel in ["x", "✓", "true", "oui"]:
            msg = f"🔔 {nom} – {adresse} – {loyer} EUR – Propriétaire : {proprio}"
            messages.append(msg)
            print(f"✅ Ajouté : {msg}")
        else:
            print("⏭️ Ignoré (pas de rappel activé)")
    except Exception as e:
        print(f"⚠️ ERREUR ligne {i+2} :", e)

# === Envoi Telegram ===
try:
    if messages:
        message = "📅 Locataires à relancer :\n" + "\n".join(messages)
    else:
        message = "✅ Aucun rappel de loyer à envoyer aujourd’hui."

    print("📨 Message généré :\n", message)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=payload)
    print(f"📤 Envoi Telegram : {response.status_code} - {response.text}")
except Exception as e:
    print("❌ ERREUR Envoi Telegram :", e)
