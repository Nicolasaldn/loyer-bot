from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from pdf.generate_quittance import generate_quittance_pdf
import os
import zipfile

# ✅ États pour le ConversationHandler
SELECT_TENANT, ENTER_PERIOD = range(2)

def handle_quittance_command(update: Update, context: CallbackContext):
    tenants = ["Thomas Cohen", "Claire Dubois", "Jean Dujardin"]  # Dynamique possible via Google Sheets
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"quittance:{name}")]
        for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text="Quel locataire pour la quittance ?",
        reply_markup=reply_markup
    )
    print("✅ [DEBUG] Commande quittance déclenchée.")
    return SELECT_TENANT

def handle_quittance_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()  # ✅ Répond immédiatement pour éviter l'erreur de délai

    tenant_name = query.data.split(":", 1)[1].strip()
    context.user_data['quittance_tenant'] = tenant_name

    # ✅ Vérifie si le texte doit vraiment être modifié
    new_text = f"Parfait, tu veux générer une quittance pour {tenant_name}.\n" \
               "Indique la période (ex: janvier 2024 ou de janvier à mars 2024)."
    
    if query.message.text != new_text:
        query.edit_message_text(new_text)
    
    print(f"✅ [DEBUG] Locataire sélectionné : {tenant_name}")
    return ENTER_PERIOD

def handle_quittance_period(update: Update, context: CallbackContext):
    tenant_name = context.user_data.get('quittance_tenant')
    period = update.message.text.strip()
    print(f"✅ [DEBUG] Période reçue : {period} pour {tenant_name}")

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné.")
        return ConversationHandler.END

    if not period:
        update.message.reply_text("❌ Erreur : aucune période fournie.")
        return ENTER_PERIOD

    try:
        if "à" in period:
            print("✅ [DEBUG] Détection d'une période multiple.")
            start_month, end_month = map(str.strip, period.split("à"))
            filepaths = generate_multiple_quittances(tenant_name, start_month, end_month)
            zip_path = create_zip_from_pdfs(filepaths, tenant_name, period)

            with open(zip_path, "rb") as zip_file:
                update.message.reply_document(document=zip_file)
            
            # ✅ Suppression des fichiers temporaires
            for path in filepaths:
                os.remove(path)
            os.remove(zip_path)
            print(f"✅ [DEBUG] Fichier ZIP envoyé : {zip_path}")
        else:
            print("✅ [DEBUG] Génération d'une quittance simple.")
            pdf_path = f"pdf/{tenant_name}_quittance_{period.replace('/', '-')}.pdf"
            generate_quittance_pdf(tenant_name, period, pdf_path)
            
            with open(pdf_path, "rb") as pdf_file:
                update.message.reply_document(document=pdf_file)
            
            os.remove(pdf_path)
            print(f"✅ [DEBUG] PDF simple envoyé : {pdf_path}")

        update.message.reply_text(
            f"✅ Quittance pour {tenant_name} générée avec succès pour la période {period}."
        )
        return ConversationHandler.END

    except Exception as e:
        print(f"❌ [DEBUG] Erreur lors de la génération : {str(e)}")
        update.message.reply_text(f"❌ Erreur lors de la génération de la quittance : {str(e)}")
        return ConversationHandler.END

# ✅ Génération de plusieurs quittances (PDFs dans un ZIP)
def generate_multiple_quittances(tenant_name, start_month, end_month):
    print(f"✅ [DEBUG] Génération de quittances de {start_month} à {end_month} pour {tenant_name}")
    from
