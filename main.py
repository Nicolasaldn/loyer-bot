from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from handlers.rappels import handle_rappel
from handlers.quittances import handle_quittance
from handlers.utils import parse_command

# === Variables globales ===
TOKEN = "YOUR_BOT_TOKEN"  # Remplace par ton vrai token
app = FastAPI()  # <- requis pour uvicorn

# === Initialisation du bot Telegram ===
bot_app = Application.builder().token(TOKEN).build()

# === Webhook FastAPI ===
@app.post("/webhook")
async def webhook(update: Update):
    await bot_app.process_update(update)
    return {"status": "ok"}

# === Routeur principal des messages ===
async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        command = parse_command(update.message.text.strip())

        if command["source"] == "rappel":
            await handle_rappel(command["args"], context)
        elif command["source"] == "quittance":
            await handle_quittance(command["args"], context)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Commande non reconnue.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Erreur : {str(e)}")

# === Handler de démarrage ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenue ! Tapez une commande comme :\n`rappel Thomas Cohen 06/05/2025`")

# === Enregistrement des handlers ===
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))
