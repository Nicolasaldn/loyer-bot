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

# Import du chatbot
from chatbot import get_chatbot_response

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    message_text = update.message.text.lower()
    state = get_user_state(user_id)

    # === RAPPEL ===
    if state.get("action") == "rappel":
        name, date_str = extract_name_and_date(message_text)
        if name and date_str:
            clear_user_state(user_id)
            filepath = generate_rappel_pdf(name, date_str)
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
            os.remove(filepath)
            return

        if name and not date_str:
            update_user_state(user_id, "name", name)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Parfait, tu veux faire un rappel pour {name.title()}. Donne-moi maintenant la date (JJ/MM/AAAA)."
            )
            return

    if "rappel" in message_text:
        set_user_state(user_id, {"action": "rappel"})
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="À quel locataire souhaites-tu envoyer un rappel ?"
        )
        return

    # === QUITTANCE ===
    if state.get("action") == "quittance" and state.get("name"):
        try:
            date_debut, date_fin = parse_quittance_period(message_text)
            clear_user_state(user_id)
            if date_debut == date_fin:
                date_obj = datetime.strptime(date_debut, "%d/%m/%Y")
                filepath = generate_quittance_pdf(state["name"], date_obj)
                context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
                os.remove(filepath)
            else:
                fichiers = generate_quittances_pdf(state["name"], date_debut, date_fin)
                zip_path = "pdf/generated/quittances.zip"
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for f in fichiers:
                        zipf.write(f, os.path.basename(f))
                        os.remove(f)
                context.bot.send_document(chat_id=update.effective_chat.id, document=open(zip_path, "rb"))
                os.remove(zip_path)
            return
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Je n’ai pas compris la période.")
            return

    if "quittance" in message_text:
        set_user_state(user_id, {"action": "quittance"})
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="À quel locataire souhaites-tu envoyer une quittance ?"
        )
        return

    # === Chatbot IA (si aucune commande spécifique) ===
    response = get_chatbot_response(message_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)
