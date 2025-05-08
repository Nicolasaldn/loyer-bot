from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from pdf.generate_quittance import generate_quittance_pdf, generate_quittances_pdf
import os
import zipfile

# ✅ États pour le ConversationHandler
SELECT_TENANT, ENTER_PERIOD = range(2)

def handle_quittance_command(update: Update, context: CallbackContext):
    tenants = ["Thomas Cohen", "Claire Dubois", "Jean Dujardin"]  # Dynamique possible via Google Sheets
    keyboard = [[InlineKeyboardButton(name, callback_data=f"quittance:{name}")] for name in tenants]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text="Quel locataire pour la quittance ?",
        reply_markup=reply_markup
    )
    print("✅ [DEBUG] Commande quittance déclenchée.")
    return SELECT_TENANT

def handle_quittance_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    try:
        tenant_name = query.data.split(":", 1)[1].strip()
        context.user_data['quittance_tenant'] = tenant_name
        print(f"✅ [DEBUG] Locataire sélectionné et enregistré : {tenant_name}")

        query.edit_message_text(
            f"Parfait, tu veux générer une quittance pour {tenant_name}.\nIndique la période (ex: janvier 2024 ou de janvier à mars 2024)."
        )
        return ENTER_PERIOD

    except IndexError:
        query.edit_message_text("❌ Erreur : Le locataire sélectionné est invalide.")
        print("❌ [DEBUG] Erreur : Nom de locataire introuvable dans le callback data.")
        return ConversationHandler.END

def handle_quittance_period(update: Update, context: CallbackContext):
    tenant_name = context.user_data.get('quittance_tenant')
    period = update.message.text.strip()
    print(f"✅ [DEBUG] Période reçue : {period} pour {tenant_name}")

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné. Utilise /quittance pour recommencer.")
        print("❌ [DEBUG] Aucun locataire sélectionné.")
        return ConversationHandler.END

    if not period:
        update.message.reply_text("❌ Erreur : aucune période fournie.")
        print("❌ [DEBUG] Période non fournie.")
        return ENTER_PERIOD

    try:
        if "à" in period:
            start_month, end_month = map(str.strip, period.split("à"))
            print(f"✅ [DEBUG] Génération de quittances multiples pour {tenant_name} de {start_month} à {end_month}.")
            filepaths = generate_quittances_pdf(tenant_name, start_month, end_month)

            zip_path = create_zip_from_pdfs(filepaths, tenant_name, period)
            print(f"✅ [DEBUG] Fichier ZIP généré : {zip_path}")

            with open(zip_path, "rb") as zip_file:
                update.message.reply_document(document=zip_file)

        else:
            print(f"✅ [DEBUG] Génération d'une quittance simple pour {tenant_name}.")
            pdf_path = generate_quittance_pdf(tenant_name, period)
            print(f"✅ [DEBUG] PDF généré : {pdf_path}")
            with open(pdf_path, "rb") as pdf_file:
                update.message.reply_document(document=pdf_file)

        update.message.reply_text(f"✅ Quittance pour {tenant_name} générée avec succès pour la période {period}.")
        return ConversationHandler.END

    except Exception as e:
        print(f"❌ [DEBUG] Erreur lors de la génération : {str(e)}")
        update.message.reply_text(f"❌ Erreur lors de la génération de la quittance : {str(e)}")
        return ConversationHandler.END
