from fastapi import FastAPI
from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = FastAPI()

# --- Load ENV VARIABLES ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_SHEET_CREDENTIALS = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON"))
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
TAB_INTERFACE = "Interface"
TAB_DB = "DB"

# --- GOOGLE SHEETS ---
def get_worksheet(tab_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEET_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.worksheet(tab_name)

def list_tenants():
    interface = get_worksheet(TAB_INTERFACE)
    values = interface.get_all_values()
    header = values[0]
    name_idx = header.index("Nom")
    return [row[name_idx] for row in values[1:] if row[name_idx]]

# --- TELEGRAM HANDLERS ---
def start(update: Update, context: CallbackContext):
    tenants = list_tenants()
    message = "Salut ! Voici les locataires disponibles :\n\n"
    for tenant in tenants:
        message += f"• {tenant}\n"
    message += "\nSouhaites-tu envoyer un rappel à quelqu’un ?"
    update.message.reply_text(message)

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if "rappel" in text:
        update.message.reply_text("À quel locataire souhaites-tu envoyer un rappel ? (Tape son nom)")
    else:
        update.message.reply_text("Je peux t’aider à envoyer des rappels de loyer. Tape /start pour commencer.")

# --- TELEGRAM APP ---
def setup_bot():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

# --- MAIN ---
if __name__ == "__main__":
    setup_bot()
