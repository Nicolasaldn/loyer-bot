from fastapi import FastAPI, Request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import os
import json

# === Imports organisés ===
from handlers.start_handler import start
from handlers.message_handler import handle_message
from handlers.quittance_handler import (
    handle_quittance_command,
    handle_quittance_selection,
    handle_quittance_period,
)
from handlers.rappel_handler import (
    handle_rappel_command,
    handle_rappel_selection,
    handle_rappel_date
)

# === Initialisation FastAPI ===
app = FastAPI()

# === Variables d'environnement ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ex: https://loyer-bot.onrender.com

# === Initialisation bot Telegram ===
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# === Ajout des handlers ===
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("quittance", handle_quittance_command))
dispatcher.add_handler(CommandHandler("rappel", handle_rappel_command))

# === Gestion des callbacks pour les boutons ===
dispatcher.add_handler(CallbackQueryHandler(handle_quittance_selection, pattern="^quittance:"))
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_selection, pattern="^rappel:"))

# === Gestion des messages directs pour les dates ===
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_quittance_period))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_rappel_date))

# === Fallback pour les messages non reconnus ===
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# === Route webhook Telegram ===
@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        print("Erreur webhook :", e)
    return {"ok": True}

# === Route test GET (optionnelle) ===
@app.get("/")
async def root():
    return {"message": "Bot opérationnel ✅"}

# === Enregistrement webhook à chaque startup ===
@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    bot.delete_webhook()
    bot.set_webhook(url=webhook_url)
    print(f"Webhook défini : {webhook_url}")
