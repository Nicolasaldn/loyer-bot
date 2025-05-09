from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from pdf.generate_quittance import generate_quittance_pdf, generate_quittances_pdf
import os
import zipfile
from datetime import datetime
import re

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
    query.answer()

    try:
        tenant_name = query.data.split(":", 1)[1].strip()
        context.user_data['quittance_tenant'] = tenant_name
        print(f"✅ [DEBUG] Locataire sélectionné et enregistré : {tenant_name}")

        query.edit_message_text(
            f"Parfait, tu veux générer une quittance pour {tenant_name}.\nIndique la période (ex: JJ/MM/AAAA ou de janvier 2025 à mars 2025)."
        )
        return ENTER_PERIOD

    except IndexError:
        print("❌ [DEBUG] Erreur : Nom de locataire introuvable dans le callback data.")
        query.edit_message_text("❌ Erreur : Le locataire sélectionné est invalide.")
        return ConversationHandler.END

def handle_quittance_period(update: Update, context: CallbackContext):
    print("✅ [DEBUG] Entrée dans handle_quittance_period")
    print(f"✅ [DEBUG] Context user_data : {context.user_data}")

    tenant_name = context.user_data.get('quittance_tenant')
    period = update.message.text.strip().lower()
    print(f"✅ [DEBUG] Période reçue : {period} pour {tenant_name}")

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné.")
        return SELECT_TENANT

    if not period:
        update.message.reply_text("❌ Erreur : aucune période fournie.")
        return ENTER_PERIOD

    try:
        output_dir = "pdf/generated/"
        os.makedirs(output_dir, exist_ok=True)

        if "à" in period:
            print("✅ [DEBUG] Reconnaissance de période multi-mois")
            start_month, end_month = map(str.strip, period.split("à"))
            filepaths = generate_quittances_pdf(tenant_name, start_month, end_month)
        else:
            print("✅ [DEBUG] Reconnaissance de période unique")
            filepaths = [generate_quittance_pdf(tenant_name, period, output_dir=output_dir)]

        if len(filepaths) > 1:
            zip_path = os.path.join(output_dir, f"Quittances_{tenant_name.replace(' ', '_')}.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file in filepaths:
                    zipf.write(file, os.path.basename(file))
                    os.remove(file)

            with open(zip_path, "rb") as zip_file:
                update.message.reply_document(document=zip_file)
            os.remove(zip_path)

        else:
            with open(filepaths[0], "rb") as pdf_file:
                update.message.reply_document(document=pdf_file)

        update.message.reply_text(
            f"✅ Quittance pour {tenant_name} générée avec succès pour la période {period}."
        )
        return ConversationHandler.END

    except Exception as e:
        print(f"❌ [DEBUG] Erreur lors de la génération : {str(e)}")
        update.message.reply_text(f"❌ Erreur lors de la génération de la quittance : {str(e)}")
        return ConversationHandler.END
