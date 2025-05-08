from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import os
import json

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
from utils.state import set_user_state, get_user_state, clear_user_state
from pdf.generate_quittance import generate_quittance_pdf
from pdf.generate_rappel import generate_rappel_pdf

# === Initialisation FastAPI ===
app = FastAPI()

# === Variables d'environnement ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# === Initialisation bot Telegram ===
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# === Gestion des callbacks ===
def handle_quittance_callback(update: Update, context: CallbackContext):
    print("✅ [DEBUG] Commande /quittance déclenchée.")
    query = update.callback_query
    query.answer()

    context.user_data.pop("rappel_tenant", None)  # Efface le rappel

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

    context.user_data.pop("quittance_tenant", None)  # Efface la quittance

    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"rappel:{name}")] for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )

# === Sélection du locataire pour rappel ===
def handle_rappel_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    tenant_name = query.data.split(":", 1)[1]
    context.user_data["rappel_tenant"] = tenant_name

    query.edit_message_text(
        text=f"Parfait, tu veux faire un rappel pour {tenant_name}.\nIndique la date souhaitée (JJ/MM/AAAA)."
    )

# === Sélection du locataire pour quittance ===
def handle_quittance_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    tenant_name = query.data.split(":", 1)[1]
    context.user_data["quittance_tenant"] = tenant_name

    query.edit_message_text(
        text=f"Parfait, tu veux générer une quittance pour {tenant_name}.\nIndique la période (ex: janvier 2024 ou de janvier à mars 2024)."
    )

# === Ajout des handlers ===
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_callback, pattern="^/rappel$"))
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_selection, pattern="^rappel:(.*)$"))
dispatcher.add_handler(CallbackQueryHandler(handle_quittance_callback, pattern="^/quittance$"))
dispatcher.add_handler(CallbackQueryHandler(handle_quittance_selection, pattern="^quittance:(.*)$"))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_quittance_period))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_rappel_date))

# === Route webhook Telegram avec Debug ===
@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
        print("==== Requête reçue ====")
        print(json.dumps(data, indent=4))

        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        print("✅ [DEBUG] Mise à jour traitée par le dispatcher.")
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
    print(f"✅ [DEBUG] Webhook défini : {webhook_url}")
    print(f"✅ [DEBUG] Réponse Webhook : {response}")
