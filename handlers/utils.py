from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
from telegram.ext import Defaults
from handlers.rappels import handle_rappel
from handlers.quittances import handle_quittance
from handlers.utils import parse_command
import os
import asyncio

# Initialisation du bot Telegram
bot_app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

# Fonction de routing des messages
async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    command = parse_command(text)

    if not command:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Commande invalide.")
        return

    if command["source"] == "rappel":
        await handle_rappel(update, context, command)
    elif command["source"] == "quittance":
        await handle_quittance(update, context, command)

# Ajout du handler pour tous les messages texte
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))

# Initialisation FastAPI
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot_app.initialize())
    asyncio.create_task(bot_app.start())

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}
