from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import os
import json

# === Imports organisés ===
from handlers.start_handler import start
from handlers.message_handler import handle_message
from handlers.rappel_handler import (
    handle_rappel_command,
    handle_rappel_selection,
    handle_rappel_date
)
from handlers.quittance_handler import (
    handle_quittance_command,
    handle_quittance_selection,
    handle_quittance_period
)
from utils.sheets import list_tenants

# === Initialisation FastAPI ===
app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# === Configuration ConversationHandler ===
quittance_handler = ConversationHandler(
    entry_points=[CommandHandler("quittance", handle_quittance_command)],
    states={
        0: [CallbackQueryHandler(handle_quittance_selection, pattern="^quittance:")],
        1: [MessageHandler(Filters.text & ~Filters.command, handle_quittance_period)]
    },
    fallbacks=[]
)

# === Ajout des handlers ===
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(quittance_handler)
dispatcher.add_handler(CommandHandler("rappel", handle_rappel_command))
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_selection, pattern="^rappel:"))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.regex(r"^\d{2}/\d{2}/\d{4}$"), handle_rappel_date))

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# === Route webhook Telegram ===
@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
        print("==== Requête reçue ====")
        print(json.dumps(data, indent=4))

        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        print("✅ [DEBUG] Mise à jour traitée par le dispatcher.")
    except Exception as e:
        print("❌ [DEBUG] Erreur webhook :", e)
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "Bot opérationnel ✅"}

@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    bot.delete_webhook()
    response = bot.set_webhook(url=webhook_url)
    print(f"✅ [DEBUG] Webhook défini : {webhook_url}")
    print(f"✅ [DEBUG] Réponse Webhook : {response}")
