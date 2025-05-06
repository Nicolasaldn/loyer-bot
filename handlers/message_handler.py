from telegram import Update
from telegram.ext import CallbackContext

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if "rappel" in text:
        context.bot.send_message(chat_id=update.effective_chat.id, text="À quel locataire souhaites-tu envoyer un rappel ?")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Tape /start pour voir la liste des locataires.")
