import os
import json
import time
import re
import requests
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF

# === Configuration ===
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SHEET_NAME = "RE - Gestion"
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# === Fonction d'envoi Telegram ===
def send_message(text):
    requests.post(f"{BASE_URL}/sendMessage", data={"chat_id": CHAT_ID, "text": text})

def send_document(file_path):
    with open(file_path, "rb") as f:
        requests.post(f"{BASE_URL}/sendDocument", data={"chat_id": CHAT_ID}, files={"document": f})

# === Fonction de parsing du message ===
def process_message(text):
    text = text.strip().lower()
    match_all = re.match(r"rappels\s+(\d{2}/\d{2}/\d{4})", text)
    if match_all:
        try:
            return {"type": "all", "date": datetime.strptime(match_all.group(1), "%d/%m/%Y")}
        except:
            return {"error": "Date invalide"}

    match_one = re.match(r"rappel\s+(.+?)\s+(\d{2}/\d{2}/\d{4})", text)
    if match_one:
        try:
            return {
                "type": "single",
                "nom": match_one.group(1).strip().title(),
                "date": datetime.strptime(match_one.group(2), "%d/%m/%Y")
            }
        except:
            return {"error": "Date invalide"}

    return {"error": "Commande non reconnue"}

# === Classe PDF ===
class AvisLoyerPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "AVIS D'ÉCHÉANCE", ln=1, align="C")
        self.set_font("Arial", "", 12)

    def generate(self, locataire, proprio_nom, proprio_adresse, date_rappel: datetime, frequence: str):
        nb_mois = 3 if frequence.lower().startswith("tri") else 1
        date_fin = (date_rappel.replace(day=1) + timedelta(days=31*nb_mois)).replace(day=1) - timedelta(days=1)
        date_exigible = (date_rappel.replace(day=1) + timedelta(days=32)).replace(day=1)
        montant_total = locataire["loyer"] * nb_mois

        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Avis d'échéance de loyer pour la période du {date_rappel.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}", ln=1, align="C")
        self.ln(5)

        self.set_font("Arial", "B", 11)
        self.cell(95, 8, "BAILLEUR :", ln=0)
        self.cell(95, 8, "LOCATAIRE :", ln=1)

        self.set_font("Arial", "", 11)
        self.cell(95, 6, proprio_nom, ln=0)
        self.cell(95, 6, locataire["nom"], ln=1)
        self.cell(95, 6, proprio_adresse, ln=0)
        self.cell(95, 6, locataire["adresse"], ln=1)
        self.ln(8)

        self.cell(0, 6, f"Fait à Paris, le {date_rappel.strftime('%d/%m/%Y')}", ln=1)
        self.ln(4)

        self.set_font("Arial", "B", 11)
        self.cell(0, 6, "ADRESSE DE LA LOCATION :", ln=1)
        self.set_font("Arial", "", 11)
        self.cell(0, 6, locataire["adresse"], ln=1)
        self.ln(6)

        self.set_fill_color(220, 220, 220)
        self.set_font("Arial", "B", 11)
        self.cell(90, 8, "LIBELLE", 1, 0, "L", 1)
        self.cell(50, 8, "MONTANT", 1, 1, "R", 1)

        self.set_font("Arial", "", 11)
        self.cell(90, 8, "Loyer TTC", 1, 0)
        self.cell(50, 8, f"{locataire['loyer']:.2f} EUR", 1, 1, "R")

        self.set_font("Arial", "B", 11)
        self.cell(90, 8, "Somme totale à régler", 1, 0)
        self.cell(50, 8, f"{montant_total:.2f} EUR", 1, 1, "R")
        self.ln(5)

        self.set_font("Arial", "", 11)
        self.cell(0, 6, f"PAIEMENT EXIGIBLE LE : {date_exigible.strftime('%d/%m/%Y')}", ln=1)
        self.ln(6)

        self.multi_cell(0, 6, "Nous vous informons que vous êtes redevable du montant de la somme détaillée ci-dessus.")
        self.multi_cell(0, 6, f"Pour rappel cette somme est à régler au plus tard le {date_exigible.strftime('%d/%m/%Y')}.")
        self.ln(4)
        self.multi_cell(0, 6, "Cet avis est une demande de paiement. Il ne peut en aucun cas servir de reçu ou de quittance de loyer.")
        return self

# === Connexion Google Sheets ===
creds_dict = json.loads(raw_creds)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
spreadsheet = client.open(SHEET_NAME)
sheet_interface = spreadsheet.worksheet("Interface")
sheet_db = spreadsheet.worksheet("DB")

# === Traitement unique d'un seul message entrant ===
updates = requests.get(f"{BASE_URL}/getUpdates").json()
messages = updates.get("result", [])

if messages:
    last_msg = messages[-1]
    text = last_msg["message"].get("text", "")
    command = process_message(text)

    if "error" in command:
        send_message("⛔ " + command["error"])

    elif command["type"] == "all":
        send_message(f"📄 Génération des rappels pour {command['date'].strftime('%d/%m/%Y')} en cours…")
        data = sheet_interface.get_all_values()[5:]  # skip headers
        db_data = sheet_db.get_all_values()[1:]  # skip headers
        db_dict = {row[0]: row[1] for row in db_data}
        for row in data:
            if len(row) >= 7 and row[6].strip().lower() == 'true':
                locataire = {
                    "nom": row[0].strip().title(),
                    "adresse": row[2].strip(),
                    "loyer": float(row[3]),
                }
                proprio = row[5].strip()
                proprio_adresse = db_dict.get(proprio, "")
                frequence = row[4].strip()
                pdf = AvisLoyerPDF()
                pdf.add_page()
                pdf.generate(locataire, proprio, proprio_adresse, command['date'], frequence)
                filename = f"/tmp/Avis_{locataire['nom'].replace(' ', '_')}_{command['date'].strftime('%Y-%m-%d')}.pdf"
                pdf.output(filename)
                send_document(filename)

    elif command["type"] == "single":
        send_message(f"📄 Génération du rappel pour {command['nom']} en cours…")
        data = sheet_interface.get_all_values()[5:]  # skip headers
        db_data = sheet_db.get_all_values()[1:]
        db_dict = {row[0]: row[1] for row in db_data}
        for row in data:
            if row[0].strip().lower() == command['nom'].lower() and row[6].strip().lower() == 'true':
                locataire = {
                    "nom": row[0].strip().title(),
                    "adresse": row[2].strip(),
                    "loyer": float(row[3]),
                }
                proprio = row[5].strip()
                proprio_adresse = db_dict.get(proprio, "")
                frequence = row[4].strip()
                pdf = AvisLoyerPDF()
                pdf.add_page()
                pdf.generate(locataire, proprio, proprio_adresse, command['date'], frequence)
                filename = f"/tmp/Avis_{locataire['nom'].replace(' ', '_')}_{command['date'].strftime('%Y-%m-%d')}.pdf"
                pdf.output(filename)
                send_document(filename)
