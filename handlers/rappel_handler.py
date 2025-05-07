from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.sheets import list_tenants
from utils.state import set_user_state, clear_user_state, get_user_state
from pdf.generate_rappel import generate_rappel_pdf
import os

def handle_rappel_command(update: Update, context: CallbackContext):
    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"rappel:{name}")]
        for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )

def handle_rappel_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data  # Ex: "rappel:Thomas Cohen"
    if not data.startswith("rappel:"):
        return

    locataire = data.split(":", 1)[1].strip()
    user_id = update.effective_user.id

    # Stocker le nom du locataire sélectionné dans l'état utilisateur
    set_user_state(user_id, {"action": "rappel", "name": locataire})

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Parfait, tu veux faire un rappel pour {locataire}.\n"
             "Indique la date souhaitée (JJ/MM/AAAA)."
    )

def handle_rappel_date(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    state = get_user_state(user_id)

    if state.get("action") == "rappel" and state.get("name"):
        locataire = state["name"]
        date_text = update.message.text.strip()

        # Génération du PDF de rappel
        try:
            filepath = generate_rappel_pdf(locataire, date_text)
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
            os.remove(filepath)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Rappel pour {locataire} généré avec succès pour la date {date_text}."
            )
        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Erreur lors de la génération du rappel : {str(e)}"
            )

        clear_user_state(user_id)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Une erreur s'est produite. Merci de recommencer avec /start."
        )
