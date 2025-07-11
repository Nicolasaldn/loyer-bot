from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils.sheets import list_tenants

def start(update: Update, context: CallbackContext):
    try:
        print("✅ [DEBUG] Tentative de connexion à Google Sheets...")
        tenants = list_tenants()
        print(f"✅ [DEBUG] Locataires récupérés : {tenants}")
    except Exception as e:
        print(f"❌ [DEBUG] Erreur de connexion à Google Sheets : {e}")
        tenants = []

    # Création du message avec la liste des locataires
    message = "Bonjour ! Comment puis-je t'assister aujourd'hui ?\n\n"
    if tenants:
        message += "Voici les locataires disponibles :\n"
        for t in tenants:
            message += f"• {t}\n"
    else:
        message += "❌ Les locataires ne sont pas disponibles actuellement."

    # Boutons inline adaptés au système de ConversationHandler
    keyboard = [
        [InlineKeyboardButton("📄 Envoyer un Rappel", callback_data="rappel:start")],
        [InlineKeyboardButton("📃 Générer une Quittance", callback_data="quittance:start")],
        [InlineKeyboardButton("👥 Ajouter un Locataire", callback_data="/ajouter_locataire")],
        [InlineKeyboardButton("🏡 Ajouter un Bailleur", callback_data="/ajouter_bailleur")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Envoi du message avec les boutons
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message + "\nChoisis une option ci-dessous :",
        reply_markup=reply_markup
    )
