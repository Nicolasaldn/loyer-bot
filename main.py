import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from handlers.rappels import handle_rappel
from handlers.quittances import handle_quittance
from handlers.utils import parse_command

# Init FastAPI + Bot
app = FastAPI()
bot_app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

# Message routing
async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.strip()
    result = parse_command(text)
if not result:
    return  # ou un message d'erreur au besoin

source, args = result


    if source == "rappel":
        await handle_rappel(update, context, *args)
    elif source == "quittance":
        await handle_quittance(update, context, *args)
    else:
        await update.message.reply_text("Commande non reconnue.")

# Register handlers
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))

@app.on_event("startup")
async def on_startup():
    await bot_app.initialize()
    await bot_app.start()

@app.on_event("shutdown")
async def on_shutdown():
    await bot_app.stop()
    await bot_app.shutdown()

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}
