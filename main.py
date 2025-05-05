import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("🧪 Démarrage du script ultra-sécurisé")

# === Chargement des variables d'environnement ===
try:
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    raw_json = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

    print("🔍 Variables récupérées :")
    print(f"  - TELEGRAM_TOKEN présent : {'✅' if BOT_TOKEN else '❌'}")
    print(f"  - TELEGRAM_CHAT_ID : {CHAT_ID}")
    print(f"  - GOOGLE_SHEET_ID : {SHEET_ID}")
    print(f"  - JSON (début brut) : {raw_json[:40]}...")

    CREDENTIALS = json.loads(raw_json)
    print("✅ JSON chargé avec succès.")
    print("🔑 Type :", CREDENTIALS.get("type"))
    print("📧 Email du bot :", CREDENTIALS.get("client_email"))
except Exception as e:
    print("❌ ERREUR chargement JSON ou variables :", e)
    raise

# === Connexion Google Sheets ===
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion Google Sheets réussie.")
except Exception as e:
    print("❌ ERREUR connexion Sheets :", e)
    raise

# === Liste des onglets disponibles ===
try:
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet_titles = [sh.title for sh in spreadsheet.worksheets()]
    print(f"📄 Feuilles disponibles dans le Google Sheet : {sheet_titles}")
except Exception as e:
    print("❌ ERREUR ouverture Google Sheet :", e)
    raise

# === Sélection de la feuille 'Interface' ===
try:
    if "Interface" not in sheet_titles:
        raise ValueError("❌ L’onglet 'Interface' n’existe pas dans le fichier Google Sheet.")
    sheet = spreadsheet.worksheet("Interface")
    print("✅ Onglet 'Interface' chargé avec succès.")
except Exception as e:
    print("❌ ERREUR chargement de la feuille 'Interface' :", e)
    raise

# === Lecture des lignes ===
try:
    rows = sheet.get_all_values()[1:]  # ignore l’en-tête
    print(f"📋 {len(rows)} lignes lues dans 'Interface'.")
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

        print(f"🔎 Ligne {i+2} : {nom} | {adresse} | {loyer} | {proprio} | Rappel={repr(rappel)}")

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
