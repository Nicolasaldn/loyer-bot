# rappel_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from pdf.generate_rappel import generate_rappel_pdf
import os

# ✅ Définition des états pour le ConversationHandler
SELECT_TENANT, ENTER_DATE = range(2)

def handle_rappel_command(update: Update, context: CallbackContext):
    tenants = ["Thomas Cohen", "Claire Dubois", "Jean Dujardin"]  # Dynamique possible via Google Sheet
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"rappel:{name}")]
        for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )
    return SELECT_TENANT

def handle_rappel_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    tenant_name = query.data.split(":", 1)[1].strip()
    context.user_data['rappel_tenant'] = tenant_name

    query.edit_message_text(
        f"Parfait, tu veux faire un rappel pour {tenant_name}.\nIndique la date souhaitée (JJ/MM/AAAA)."
    )
    return ENTER_DATE

def handle_rappel_date(update: Update, context: CallbackContext):
    tenant_name = context.user_data.get('rappel_tenant')
    date = update.message.text.strip()

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné.")
        return ConversationHandler.END

    if not date:
        update.message.reply_text("❌ Erreur : aucune date fournie.")
        return ENTER_DATE

    try:
        # ✅ Génération du PDF
        pdf_path = f"pdf/{tenant_name}_rappel_{date.replace('/', '-')}.pdf"
        generate_rappel_pdf(tenant_name, date, 500, pdf_path)  # Montant par défaut

        # ✅ Envoi du PDF
        with open(pdf_path, "rb") as pdf_file:
            update.message.reply_document(document=pdf_file)
        
        # ✅ Suppression du PDF après envoi
        os.remove(pdf_path)

        update.message.reply_text(
            f"✅ Rappel pour {tenant_name} généré avec succès pour la date {date}."
        )
        return ConversationHandler.END

    except Exception as e:
        update.message.reply_text(f"❌ Erreur lors de la génération du rappel : {str(e)}")
        return ConversationHandler.END
