import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from handlers.rappels import handle_rappel
from handlers.quittances import handle_quittance
from handlers.utils import parse_command

# Configuration des logs
logging.basicConfig(level=logging.INFO)

# Vérifie le token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN or ":" not in TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN est mal configuré. Vérifie Render.")

# Création de l'application Telegram
bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Ajout du message handler
bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), lambda u, c: route_message(u, c)))

# Création de l'application FastAPI
app = FastAPI()

# Handler Telegram
async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        command = parse_command(text)
        if not command:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Commande non reconnue.")
            return

        source = command["source"]
        if source == "rappel":
            await handle_rappel(update, context, command)
        elif source == "quittance":
            await handle_quittance(update, context, command)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Commande invalide.")
    except Exception as e:
        logging.exception("Erreur dans le handler Telegram")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Erreur lors du traitement.")

# Endpoint webhook
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.initialize()
    await bot_app.process_update(update)
    return {"status": "ok"}

# Endpoint test GET
@app.get("/")
def read_root():
    return {"message": "Bot is running ✅"}
