from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from pdf.avis import AvisLoyerPDF
from handlers.utils import get_sheet_data, get_db_dict
import os
import logging

logger = logging.getLogger(__name__)

async def handle_rappel(update: Update, context: ContextTypes.DEFAULT_TYPE, command):
    chat_id = update.message.chat_id

    # ✅ Vérifie la présence de la date
    if command["date"] is None:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Merci d’indiquer une date valide, ex : `rappel Thomas Cohen 07/05/2025`"
        )
        return

    # ✅ Récupération des données
    data = get_sheet_data()
    db_dict = get_db_dict()

    logger.info(f"[DEBUG] Commande reçue : {command}")
    logger.info(f"[DEBUG] Liste des noms de la feuille : {[row['Nom'] for row in data if 'Nom' in row]}")

    # ✅ Rappel à tous
    if command["type"] == "all":
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📄 Génération des rappels pour {command['date'].strftime('%d/%m/%Y')}..."
        )
        for row in data:
            if "Nom" in row:
                await generate_and_send_pdf(row, db_dict, command["date"], context, chat_id)

    # ✅ Rappel ciblé
    elif command["type"] == "single":
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📄 Génération du rappel pour {command['nom']}..."
        )
        found = False
        for row in data:
            if "Nom" in row and command["nom"].lower() in row["Nom"].strip().lower():
                logger.info(f"[DEBUG] ➤ LOCATAIRE TROUVÉ : {row['Nom']}")
                found = True
                await generate_and_send_pdf(row, db_dict, command["date"], context, chat_id)
                break
        if not found:
            logger.warning(f"[DEBUG] ❌ Locataire introuvable pour : {command['nom']}")
            await context.bot.send_message(chat_id=chat_id, text="❌ Locataire introuvable.")

async def generate_and_send_pdf(row, db_dict, date_rappel, context, chat_id):
    try:
        if date_rappel is None:
            logger.error("[ERREUR] date_rappel est None")
            await context.bot.send_message(chat_id=chat_id, text="❌ Date de rappel manquante.")
            return

        nom = row["Nom"].strip().title()
        logger.info(f"[DEBUG] ➤ Début pour : {nom}")

        locataire = {
            "nom": nom,
            "adresse": row["Adresse"].strip(),
            "loyer": float(row["Loyer TTC (€)"])
        }
        logger.info(f"[DEBUG] ➤ Loyer : {locataire['loyer']} €")

        proprio = row["Proprietaire"].strip()
        proprio_adresse = db_dict.get(proprio, "[adresse non trouvée]")
        frequence = row["Fréquence"].strip()

        pdf = AvisLoyerPDF()
        pdf.add_page()
        pdf.generate(locataire, proprio, proprio_adresse, date_rappel, frequence)

        filename = f"/tmp/Avis_{nom.replace(' ', '_')}_{date_rappel.strftime('%Y-%m-%d')}.pdf"
        pdf.output(filename)
        logger.info(f"[DEBUG] ➤ PDF sauvegardé dans : {filename}")

        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=chat_id,
                document=InputFile(f),
                filename=os.path.basename(filename)
            )
            logger.info(f"[DEBUG] ✅ PDF envoyé à Telegram")

    except Exception as e:
        logger.error(f"[ERREUR] ❌ Exception lors du traitement : {e}")
        await context.bot.send_message(chat_id=chat_id, text="❌ Erreur lors de la génération ou de l'envoi du PDF.")
