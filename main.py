from fastapi import FastAPI, Request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = FastAPI()

# --- ENV ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_SHEET_CREDENTIALS = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON"))
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
TAB_INTERFACE = "Interface"

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# --- Google Sheets ---
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

# --- Handlers ---
def start(update: Update, context):
    tenants = list_tenants()
    message = "Voici les locataires disponibles :\n"
    for t in tenants:
        message += f"• {t}\n"
    message += "\nSouhaites-tu envoyer un rappel à quelqu’un ?"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def handle_message(update: Update, context):
    txt = update.message.text.lower()
    if "rappel" in txt:
        context.bot.send_message(chat_id=update.effective_chat.id, text="À quel locataire souhaites-tu envoyer un rappel ?")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Je peux t’aider à envoyer des rappels. Tape /start.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# --- Webhook route ---
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"ok": True}

# --- Set webhook at startup ---
@app.on_event("startup")
async def set_webhook():
    webhook_url = os.getenv("WEBHOOK_URL") + "/webhook"
    bot.set_webhook(url=webhook_url)
