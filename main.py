from fastapi import FastAPI, Request
from telegram import Bot, Update
from telegram.ext import (
    Dispatcher, CommandHandler, MessageHandler, Filters,
    CallbackQueryHandler, CallbackContext, ConversationHandler
)
import os
from datetime import datetime

# === Imports organisés ===
from handlers.start_handler import start
from handlers.message_handler import handle_message
from handlers.rappel_handler import (
    handle_rappel_command,
    handle_rappel_selection,
    handle_rappel_date,
    SELECT_TENANT, ENTER_DATE
)
from handlers.quittance_handler import (
    handle_quittance_command,
    handle_quittance_selection,
    handle_quittance_period,
    SELECT_TENANT_QUITTANCE, ENTER_PERIOD
)
from handlers.locataire_bailleur_handler import (
    handle_add_tenant,
    handle_add_tenant_name, handle_add_tenant_email, handle_add_tenant_address,
    handle_add_tenant_rent, handle_add_tenant_frequency, handle_add_tenant_landlord,
    handle_add_landlord, handle_add_landlord_name, handle_add_landlord_address,
    ADD_TENANT_NAME, ADD_TENANT_EMAIL, ADD_TENANT_ADDRESS, ADD_TENANT_RENT,
    ADD_TENANT_FREQUENCY, ADD_TENANT_LANDLORD, ADD_LANDLORD_NAME, ADD_LANDLORD_ADDRESS
)

# === Initialisation FastAPI et Bot ===
app = FastAPI()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# === Handler par défaut pour texte sans contexte ===
def handle_text_message(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Erreur : aucune action en cours. Utilise /start.")

# === Commande /start ===
dispatcher.add_handler(CommandHandler("start", start))

# === Conversation: Rappel ===
dispatcher.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler("rappel", handle_rappel_command),
        CallbackQueryHandler(handle_rappel_command, pattern="^rappel:start$")
    ],
    states={
        SELECT_TENANT: [CallbackQueryHandler(handle_rappel_selection, pattern="^rappel:")],
        ENTER_DATE: [MessageHandler(Filters.text & ~Filters.command, handle_rappel_date)],
    },
    fallbacks=[]
))

# === Conversation: Quittance ===
dispatcher.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler("quittance", handle_quittance_command),
        CallbackQueryHandler(handle_quittance_command, pattern="^quittance:start$")
    ],
    states={
        SELECT_TENANT_QUITTANCE: [CallbackQueryHandler(handle_quittance_selection, pattern="^quittance:")],
        ENTER_PERIOD: [MessageHandler(Filters.text & ~Filters.command, handle_quittance_period)],
    },
    fallbacks=[]
))

# === Conversation: Ajouter locataire (commande et bouton inline) ===
dispatcher.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler("ajouter_locataire", handle_add_tenant),
        CallbackQueryHandler(handle_add_tenant, pattern="^/ajouter_locataire$")
    ],
    states={
        ADD_TENANT_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_name)],
        ADD_TENANT_EMAIL: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_email)],
        ADD_TENANT_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_address)],
        ADD_TENANT_RENT: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_rent)],
        ADD_TENANT_FREQUENCY: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_frequency)],
        ADD_TENANT_LANDLORD: [MessageHandler(Filters.text & ~Filters.command, handle_add_tenant_landlord)],
    },
    fallbacks=[]
))

# === Conversation: Ajouter bailleur (commande et bouton inline) ===
dispatcher.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler("ajouter_bailleur", handle_add_landlord),
        CallbackQueryHandler(handle_add_landlord, pattern="^/ajouter_bailleur$")
    ],
    states={
        ADD_LANDLORD_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_add_landlord_name)],
        ADD_LANDLORD_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, handle_add_landlord_address)],
    },
    fallbacks=[]
))

# === Fallback pour tout texte hors conversation ===
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))

# === Webhook Telegram (POST) ===
@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        print("❌ [DEBUG] Erreur webhook :", e)
    return {"ok": True}

# === Ping HTTP (GET) ===
@app.get("/")
async def root():
    return {"message": "Bot opérationnel ✅"}

# === Au démarrage de FastAPI ===
@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    bot.delete_webhook()
    bot.set_webhook(url=webhook_url)
