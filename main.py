from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
import os

from handlers.rappels import handle_rappel
from handlers.quittances import handle_quittance
from handlers.utils import parse_command

# Chargement des variables d'environnement
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialisation du bot Telegram
bot_app = Application.builder().token(TOKEN).build()
app = FastAPI()

# Gestion des messages Telegram entrants
@bot_app.message_handler()
async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    source, args = parse_command(text)

    if source == "rappel":
        await handle_rappel(update, context, *args)
    elif source == "quittance":
        await handle_quittance(update, context, *args)
    else:
        await update.message.reply_text("Commande inconnue. Utilise 'rappel' ou 'quittance'.")

# Endpoint FastAPI pour recevoir les webhooks Telegram
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

# Définition du webhook à l'initialisation
@app.on_event("startup")
async def startup():
    await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
