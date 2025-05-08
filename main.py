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

    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"rappel:{name}")] for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )

def handle_rappel_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    tenant_name = query.data.split(":", 1)[1]
    context.user_data["rappel_tenant"] = tenant_name

    query.edit_message_text(
        text=f"Parfait, tu veux faire un rappel pour {tenant_name}.\nIndique la date souhaitée (JJ/MM/AAAA)."
    )

def handle_rappel_date(update: Update, context: CallbackContext):
    tenant_name = context.user_data.get("rappel_tenant")
    date = update.message.text.strip()

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné.")
        return

    try:
        output_dir = "pdf/generated/"
        os.makedirs(output_dir, exist_ok=True)

        pdf_path = generate_rappel_pdf(tenant_name, date, output_dir=output_dir)
        with open(pdf_path, "rb") as pdf_file:
            update.message.reply_document(document=pdf_file)
        os.remove(pdf_path)

        update.message.reply_text(f"✅ Rappel pour {tenant_name} généré avec succès pour la date {date}.")

    except Exception as e:
        print(f"❌ [DEBUG] Erreur lors de la génération du rappel : {str(e)}")
        update.message.reply_text(f"❌ Erreur lors de la génération du rappel : {str(e)}")

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
