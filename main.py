import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters
import uvicorn
from handlers.rappels import handle_rappel
from handlers.utils import parse_command

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = FastAPI()
telegram_app = Application.builder().token(BOT_TOKEN).build()


async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    text = update.message.text
    command = parse_command(text)

    if command.get("source") == "rappel":
        await handle_rappel(update, context, command)
    elif command.get("source") == "quittance":
        await context.bot.send_message(chat_id=update.message.chat_id, text="📦 Fonction quittance à venir…")
    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text="⛔ Commande non reconnue.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue sur le bot de gestion locative !\n\n"
        "Voici ce que tu peux faire :\n"
        "- `rappel thomas cohen 06/05/2025`\n"
        "- `rappels 06/05/2025`\n"
        "- `quittance thomas cohen mai`\n"
        "- `quittance thomas cohen de janvier 2023 à mars 2023`\n\n"
        "Je t'enverrai les fichiers PDF ou ZIP selon le cas.\n",
        parse_mode="Markdown"
    )

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", start))

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
