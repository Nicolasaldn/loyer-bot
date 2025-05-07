from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from utils.sheets import list_tenants

def start(update: Update, context: CallbackContext):
    tenants = list_tenants()
    
    # Création du message avec la liste des locataires
    message = "Bonjour ! Comment puis-je t'assister aujourd'hui ?\n\n"
    message += "Voici les locataires disponibles :\n"
    for t in tenants:
        message += f"• {t}\n"
    
    # Menu avec les options disponibles
    keyboard = [
        ["/rappel", "/quittance"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Envoi du message avec les options
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message + "\nChoisis une option ci-dessous :",
        reply_markup=reply_markup
    )
