from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.sheets import list_tenants
from utils.state import set_user_state


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
