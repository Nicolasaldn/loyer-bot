from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.sheets import list_tenants
from utils.state import set_user_state, clear_user_state, get_user_state
from pdf.generate_quittance import generate_quittance_pdf
from datetime import datetime
import os

def handle_quittance_command(update: Update, context: CallbackContext):
    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"quittance:{name}")]
        for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Quel locataire pour la quittance ?",
        reply_markup=reply_markup
    )

def handle_quittance_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data  # Ex: "quittance:Thomas Cohen"
    if not data.startswith("quittance:"):
        return

    locataire = data.split(":", 1)[1].strip()
    user_id = update.effective_user.id

    set_user_state(user_id, {"action": "quittance", "name": locataire})

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Parfait, tu veux une quittance pour {locataire}.\n"
             "Pour quelle période ?\n"
             "Tu peux m’écrire par exemple :\n→ janvier 2024\n→ de janvier 2024 à mars 2024"
    )


def handle_quittance_period(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    state = get_user_state(user_id)

    if state.get("action") == "quittance" and state.get("name"):
        locataire = state["name"]
        date_text = update.message.text.strip()

        # Génération du PDF de quittance
        filepath = generate_quittance_pdf(locataire, date_text)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
        os.remove(filepath)
        clear_user_state(user_id)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Une erreur s'est produite. Merci de recommencer avec /start."
        )
