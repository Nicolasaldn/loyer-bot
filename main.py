import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

from handlers.rappels import handle_rappel
from handlers.quittances import handle_quittance
from handlers.utils import parse_command
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot_app = Application.builder().token(TELEGRAM_TOKEN).build()

app = FastAPI()

# 🎯 Handler principal : route tous les messages texte
async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = parse_command(update.message.text)
    if command["source"] == "rappel":
        await handle_rappel(update, context, command)
    elif command["source"] == "quittance":
        await handle_quittance(update, context, command)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Commande non reconnue."
        )

# 🔁 Enregistrement du handler
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))

# 🔗 Webhook FastAPI
@app.on_event("startup")
async def startup():
    await bot_app.initialize()
    await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return "ok"
