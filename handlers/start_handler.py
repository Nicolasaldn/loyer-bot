from telegram import Update
from telegram.ext import CallbackContext
from utils.sheets import list_tenants

def start(update: Update, context: CallbackContext):
    tenants = list_tenants()
    message = "Voici les locataires disponibles :\n"
    for t in tenants:
        message += f"• {t}\n"
    message += "\nSouhaites-tu envoyer un rappel à quelqu’un ?"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
