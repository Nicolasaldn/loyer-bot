from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
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

# === Variables d'environnement ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# === Initialisation bot Telegram ===
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# === Gestion des callbacks ===
dispatcher.add_handler(CommandHandler("start", start))

# ✅ Gestion des rappels
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_command, pattern="^/rappel$"))
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_selection, pattern="^rappel:"))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.regex(r"^\d{2}/\d{2}/\d{4}$"), handle_rappel_date))

# ✅ Gestion des quittances
dispatcher.add_handler(CallbackQueryHandler(handle_quittance_command, pattern="^/quittance$"))
dispatcher.add_handler(CallbackQueryHandler(handle_quittance_selection, pattern="^quittance:"))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.regex(r"^\d{2}/\d{2}/\d{4}$"), handle_quittance_period))

# === Route webhook Telegram avec Debug ===
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

# === Enregistrement webhook à chaque startup avec Debug ===
@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    bot.delete_webhook()
    response = bot.set_webhook(url=webhook_url)
    print(f"✅ [DEBUG] Webhook défini : {webhook_url}")
    print(f"✅ [DEBUG] Réponse Webhook : {response}")
