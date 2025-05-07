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

# === Initialisation FastAPI ===
app = FastAPI()

# === Variables d'environnement ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# === Initialisation bot Telegram ===
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# === Gestion des callbacks ===
def handle_rappel_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"rappel:{name}")]
        for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )

def handle_quittance_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"quittance:{name}")]
        for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text="Quel locataire pour la quittance ?",
        reply_markup=reply_markup
    )

# === Gestion des actions de rappel ===
def handle_rappel_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    locataire = query.data.split(":")[1]
    set_user_state(update.effective_user.id, {"action": "rappel", "name": locataire})
    
    query.edit_message_text(
        text=f"Parfait, tu veux faire un rappel pour {locataire}.\n"
             "Indique la date souhaitée (JJ/MM/AAAA)."
    )

def handle_rappel_date(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    state = get_user_state(user_id)

    if state.get("action") == "rappel" and state.get("name"):
        locataire = state["name"]
        date_text = update.message.text.strip()

        try:
            # Appelle ta fonction pour générer le PDF de rappel
            filepath = generate_rappel_pdf(locataire, date_text)
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
            os.remove(filepath)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Rappel pour {locataire} généré avec succès pour la date {date_text}."
            )
        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Erreur lors de la génération du rappel : {str(e)}"
            )

        clear_user_state(user_id)

# === Ajout des handlers ===
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_callback, pattern="^/rappel$"))
dispatcher.add_handler(CallbackQueryHandler(handle_quittance_callback, pattern="^/quittance$"))
dispatcher.add_handler(CallbackQueryHandler(handle_rappel_selection, pattern="^rappel:"))
dispatcher.add_handler(CallbackQueryHandler(handle_quittance_selection, pattern="^quittance:"))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_rappel_date))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_quittance_period))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# === Route webhook Telegram avec Debug ===
@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
        print("==== Requête reçue ====")
        print(json.dumps(data, indent=4))
        
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        print("Erreur webhook :", e)
    return {"ok": True}

# === Route test GET (optionnelle) ===
@app.get("/")
async def root():
    return {"message": "Bot opérationnel ✅"}

# === Enregistrement webhook à chaque startup avec Debug ===
@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    bot.delete_webhook()
    response = bot.set_webhook(url=webhook_url)
    print(f"Webhook défini : {webhook_url}")
    print(f"Réponse Webhook : {response}")
