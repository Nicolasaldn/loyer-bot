import os
import json
import re
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === Configuration ===
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
SHEET_NAME = "RE - Gestion"
raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")

# === Connexion Google Sheets ===
creds_dict = json.loads(raw_creds)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
spreadsheet = client.open(SHEET_NAME)
sheet_interface = spreadsheet.worksheet("Interface")
sheet_db = spreadsheet.worksheet("DB")

# === Classe PDF ===
class AvisLoyerPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "AVIS D'ÉCHÉANCE", ln=1, align="C")

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

# === Commande reçue ===
def parse_command(text):
    match_all = re.match(r"rappels\s+(\d{2}/\d{2}/\d{4})", text.lower())
    if match_all:
        return {"type": "all", "date": datetime.strptime(match_all.group(1), "%d/%m/%Y")}
    match_one = re.match(r"rappel\s+(.+?)\s+(\d{2}/\d{2}/\d{4})", text.lower())
    if match_one:
        return {
            "type": "single",
            "nom": match_one.group(1).strip().title(),
            "date": datetime.strptime(match_one.group(2), "%d/%m/%Y")
        }
    return {"error": "Commande non reconnue."}

# === Handler principal ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id
    command = parse_command(text)

    if "error" in command:
        await context.bot.send_message(chat_id=chat_id, text="⛔ " + command["error"])
        return

    db_data = sheet_db.get_all_values()[1:]
    db_dict = {row[0]: row[1] for row in db_data}
    data = sheet_interface.get_all_values()[5:]

    if command["type"] == "all":
        await context.bot.send_message(chat_id=chat_id, text=f"📄 Génération des rappels pour {command['date'].strftime('%d/%m/%Y')}...")
        for row in data:
            if len(row) >= 7 and row[6].strip().lower() == 'true':
                await generate_and_send_pdf(row, db_dict, command['date'], context, chat_id)

    elif command["type"] == "single":
        await context.bot.send_message(chat_id=chat_id, text=f"📄 Génération du rappel pour {command['nom']}...")
        for row in data:
            if row[0].strip().lower() == command['nom'].lower() and row[6].strip().lower() == 'true':
                await generate_and_send_pdf(row, db_dict, command['date'], context, chat_id)
                return
        await context.bot.send_message(chat_id=chat_id, text="❌ Locataire introuvable ou non à relancer.")

# === Génération PDF ===
async def generate_and_send_pdf(row, db_dict, date_rappel, context, chat_id):
    locataire = {
        "nom": row[0].strip().title(),
        "adresse": row[2].strip(),
        "loyer": float(row[3])
    }
    proprio = row[5].strip()
    proprio_adresse = db_dict.get(proprio, "")
    frequence = row[4].strip()

    pdf = AvisLoyerPDF()
    pdf.add_page()
    pdf.generate(locataire, proprio, proprio_adresse, date_rappel, frequence)
    filename = f"/tmp/Avis_{locataire['nom'].replace(' ', '_')}_{date_rappel.strftime('%Y-%m-%d')}.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        await context.bot.send_document(chat_id=chat_id, document=InputFile(f), filename=os.path.basename(filename))

# === Lancement du bot ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot prêt à recevoir des messages…")
    app.run_polling()
