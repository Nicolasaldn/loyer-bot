from telegram import Update
from telegram.ext import CallbackContext
from utils.sheets import list_tenants
from utils.state import (
    set_user_state,
    get_user_state,
    clear_user_state,
    update_user_state
)
from utils.parser import extract_name_and_date, parse_quittance_period
from pdf.generate_rappel import generate_rappel_pdf
from pdf.generate_quittance import generate_quittance_pdf, generate_quittances_pdf
from datetime import datetime
import os
import zipfile

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    message_text = update.message.text.lower()
    state = get_user_state(user_id)

    # === RAPPEL ===
    name, date_str = extract_name_and_date(message_text)

    if name and date_str and state.get("action") == "rappel":
        clear_user_state(user_id)
        filepath = generate_rappel_pdf(name, date_str)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
        os.remove(filepath)  # Supprimer après envoi
        return

    if "rappel" in message_text:
        set_user_state(user_id, {"action": "rappel"})
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="À quel locataire souhaites-tu envoyer un rappel ?"
        )
        return

    if state.get("action") == "rappel" and name and not date_str:
        update_user_state(user_id, "name", name)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Parfait, tu veux faire un rappel pour {name.title()}. Donne-moi maintenant la date (JJ/MM/AAAA)."
        )
        return

    if state.get("action") == "rappel" and state.get("name") and date_str:
        name = state["name"]
        clear_user_state(user_id)
        filepath = generate_rappel_pdf(name, date_str)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
        os.remove(filepath)  # Supprimer après envoi
        return

    # === QUITTANCE ===
    if state.get("action") == "quittance" and state.get("name"):
        try:
            date_debut, date_fin = parse_quittance_period(message_text)
        except ValueError:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Je n’ai pas compris la période. Essaie par exemple :\n→ janvier 2024\n→ de février 2024 à avril 2024"
            )
            return

        nom = state["name"]
        clear_user_state(user_id)

        # Un mois : 1 quittance
        if date_debut == date_fin:
            date_obj = datetime.strptime(date_debut, "%d/%m/%Y")
            filepath = generate_quittance_pdf(nom, date_obj)
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
            os.remove(filepath)  # Supprimer après envoi
        else:
            # Plusieurs mois : génération des PDF et création du ZIP
            fichiers = generate_quittances_pdf(nom, date_debut, date_fin)
            zip_path = "pdf/generated/quittances.zip"
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for f in fichiers:
                    zipf.write(f, os.path.basename(f))
                    os.remove(f)  # Supprimer chaque PDF après ajout au ZIP
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(zip_path, "rb"))
            os.remove(zip_path)  # Supprimer le ZIP après envoi
        return

    # === Fallback ===
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Tape /start pour voir la liste des locataires."
    )
