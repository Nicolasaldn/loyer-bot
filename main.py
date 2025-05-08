from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import os
import json
from datetime import datetime

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
from pdf.generate_quittance import generate_quittance_pdf, generate_quittances_pdf
from pdf.generate_rappel import generate_rappel_pdf

# === Initialisation FastAPI ===
app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# === Gestion des callbacks ===
def handle_quittance_callback(update: Update, context: CallbackContext):
    print("✅ [DEBUG] Commande /quittance déclenchée.")
    query = update.callback_query
    query.answer()

    context.user_data.pop("rappel_tenant", None)

    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"quittance:{name}")] for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="Quel locataire pour la quittance ?",
        reply_markup=reply_markup
    )

# === Gestion des rappels ===
def handle_rappel_callback(update: Update, context: CallbackContext):
    print("✅ [DEBUG] Commande /rappel déclenchée.")
    query = update.callback_query
    query.answer()

    context.user_data.pop("quittance_tenant", None)

    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"rappel:{name}")] for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )

# === Fonction de parsing des périodes de quittance ===
def parse_quittance_period(period: str):
    period = period.lower().strip()

    if "de" in period and "à" in period:
        parts = period.replace("de ", "").split(" à ")
        start, end = parts[0].strip(), parts[1].strip()

        try:
            start_date = datetime.strptime(start, "%d/%m/%Y")
            end_date = datetime.strptime(end, "%d/%m/%Y")
        except ValueError:
            months = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                      "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12}

            def month_to_date(month_str):
                month = months.get(month_str.split()[0], 1)
                year = int(month_str.split()[-1])
                return datetime(year, month, 1)

            start_date = month_to_date(start)
            end_date = month_to_date(end)

        if start_date > end_date:
            raise ValueError("La date de début doit être avant la date de fin.")

        return start_date, end_date

    try:
        single_date = datetime.strptime(period, "%d/%m/%Y")
        return single_date, single_date
    except ValueError:
        raise ValueError("Format de période invalide.")

# === Gestion des périodes et dates ===
def handle_text_message(update: Update, context: CallbackContext):
    if not update.message or not update.message.text:
        return

    message_text = update.message.text.strip()

    if "quittance_tenant" in context.user_data:
        handle_quittance_period(update, context)
    elif "rappel_tenant" in context.user_data:
        handle_rappel_date(update, context)
    else:
        update.message.reply_text("❌ Erreur : aucune action en cours. Utilise /start.")

# === Ajout des handlers ===
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_callback, pattern="^/rappel$"))
dispatcher.add_handler(CallbackQueryHandler(handle_quittance_callback, pattern="^/quittance$"))
dispatcher.add_handler(CallbackQueryHandler(handle_message, pattern="^(rappel|quittance):"))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))

# === Route webhook Telegram avec Debug ===
@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        print("❌ [DEBUG] Erreur webhook :", e)
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "Bot opérationnel ✅"}

@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    bot.delete_webhook()
    response = bot.set_webhook(url=webhook_url)
