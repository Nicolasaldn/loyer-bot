from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, ConversationHandler
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
from handlers.locataire_bailleur_handler import (
    handle_add_tenant,
    handle_add_tenant_name, handle_add_tenant_email, handle_add_tenant_address,
    handle_add_tenant_rent, handle_add_tenant_frequency, handle_add_tenant_landlord,
    handle_add_landlord, handle_add_landlord_name, handle_add_landlord_address
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
    keyboard = [[InlineKeyboardButton(name, callback_data=f"quittance:{name}")] for name in tenants]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="Quel locataire pour la quittance ?",
        reply_markup=reply_markup
    )

def handle_rappel_callback(update: Update, context: CallbackContext):
    print("✅ [DEBUG] Commande /rappel déclenchée.")
    query = update.callback_query
    query.answer()

    context.user_data.pop("quittance_tenant", None)

    tenants = list_tenants()
    keyboard = [[InlineKeyboardButton(name, callback_data=f"rappel:{name}")] for name in tenants]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )

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
dispatcher.add_handler(CallbackQueryHandler(handle_add_tenant, pattern="^/ajouter_locataire$"))
dispatcher.add_handler(CallbackQueryHandler(handle_add_landlord, pattern="^/ajouter_bailleur$"))

# === ConversationHandler pour ajouter locataire ===
dispatcher.add_handler(ConversationHandler(
    entry_points=[CommandHandler("ajouter_locataire", handle_add_tenant)],
    states={
        0: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_name)],
        1: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_email)],
        2: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_address)],
        3: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_rent)],
        4: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_frequency)],
        5: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_landlord)]
    },
    fallbacks=[]
))

# === ConversationHandler pour ajouter bailleur ===
dispatcher.add_handler(ConversationHandler(
    entry_points=[CommandHandler("ajouter_bailleur", handle_add_landlord)],
    states={
        0: [MessageHandler(Filters.text & ~Filters.command, handle_add_landlord_name)],
        1: [MessageHandler(Filters.text & ~Filters.command, handle_add_landlord_address)]
    },
    fallbacks=[]
))

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))

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
    bot.set_webhook(url=webhook_url)
