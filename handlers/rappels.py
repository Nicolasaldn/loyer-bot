from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from pdf.avis import AvisLoyerPDF
from handlers.utils import get_sheet_data, get_db_dict
import os

async def handle_rappel(update: Update, context: ContextTypes.DEFAULT_TYPE, command):
    chat_id = update.message.chat_id
    data = get_sheet_data()[5:]  # ignore l’en-tête + lignes intro
    db_dict = get_db_dict()

    if command["type"] == "all":
        await context.bot.send_message(chat_id=chat_id, text=f"📄 Génération des rappels pour {command['date'].strftime('%d/%m/%Y')}...")
        for row in data:
            if len(row) >= 9:
                await generate_and_send_pdf(row, db_dict, command['date'], context, chat_id)

    elif command["type"] == "single":
        await context.bot.send_message(chat_id=chat_id, text=f"📄 Génération du rappel pour {command['nom']}...")
        found = False
        for row in data:
            if command['nom'].lower() in row[0].strip().lower():
                found = True
                await generate_and_send_pdf(row, db_dict, command['date'], context, chat_id)
                break
        if not found:
            await context.bot.send_message(chat_id=chat_id, text="❌ Locataire introuvable.")

async def generate_and_send_pdf(row, db_dict, date_rappel, context, chat_id):
    try:
        print(f"[DEBUG] ➤ Début pour : {row[0]}")
        locataire = {
            "nom": row[0].strip().title(),
            "adresse": row[2].strip(),
            "loyer": float(row[3])
        }
        print(f"[DEBUG] ➤ Loyer : {locataire['loyer']} €")

        proprio = row[5].strip()
        proprio_adresse = db_dict.get(proprio, "[adresse non trouvée]")
        frequence = row[4].strip()

        pdf = AvisLoyerPDF()
        pdf.add_page()
        pdf.generate(locataire, proprio, proprio_adresse, date_rappel, frequence)

        filename = f"/tmp/Avis_{locataire['nom'].replace(' ', '_')}_{date_rappel.strftime('%Y-%m-%d')}.pdf"
        pdf.output(filename)
        print(f"[DEBUG] ➤ PDF sauvegardé dans : {filename}")

        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=chat_id,
                document=InputFile(f),
                filename=os.path.basename(filename)
            )
            print(f"[DEBUG] ✅ PDF envoyé à Telegram")

    except Exception as e:
        print(f"[ERREUR] ❌ Exception lors du traitement : {e}")
        await context.bot.send_message(chat_id=chat_id, text="❌ Erreur lors de la génération ou de l'envoi du PDF.")
