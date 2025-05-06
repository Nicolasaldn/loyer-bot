import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes
from handlers.rappels import handle_rappel
from handlers.quittances import handle_quittance
from handlers.utils import parse_command

# Init FastAPI app
app = FastAPI()

# Init Telegram bot app
bot_app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    update = Update.de_json(body, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}

@bot_app.message_handler()
async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    command = parse_command(text)

    if not command:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Commande non reconnue.")
        return

    if command["source"] == "rappel":
        await handle_rappel(update, context, command)
    elif command["source"] == "quittance":
        await handle_quittance(update, context, command)
