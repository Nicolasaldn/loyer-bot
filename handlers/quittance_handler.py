from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from pdf.generate_quittance import generate_quittance_pdf, generate_quittances_pdf
import os
import zipfile
from datetime import datetime
import re

# ✅ États pour le ConversationHandler
SELECT_TENANT, ENTER_PERIOD = range(2)

FRENCH_MONTHS = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12
}

def handle_quittance_command(update: Update, context: CallbackContext):
    tenants = ["Thomas Cohen", "Claire Dubois", "Jean Dujardin"]
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

    tenant_name = query.data.split(":", 1)[1].strip()
    context.user_data['quittance_tenant'] = tenant_name
    print(f"✅ [DEBUG] Locataire sélectionné : {tenant_name}")

    query.edit_message_text(
        f"Parfait, tu veux générer une quittance pour {tenant_name}.\nIndique la période (ex: janvier 2025 ou de janvier 2025 à mars 2025)."
    )
    return ENTER_PERIOD

def handle_quittance_period(update: Update, context: CallbackContext):
    tenant_name = context.user_data.get('quittance_tenant')
    period = update.message.text.strip().lower()

    print(f"✅ [DEBUG] Période reçue : {period} pour {tenant_name}")

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné.")
        return SELECT_TENANT

    try:
        if "à" in period:
            start, end = map(str.strip, period.split("à"))
        else:
            start = end = period

        if re.match(r"\d{2}/\d{2}/\d{4}", start):
            start_date = datetime.strptime(start, "%d/%m/%Y")
            end_date = datetime.strptime(end, "%d/%m/%Y")
        else:
            start_date = datetime(datetime.now().year, FRENCH_MONTHS[start.split()[0]], 1)
            end_date = datetime(datetime.now().year, FRENCH_MONTHS[end.split()[0]], 28)

        if start_date.month == end_date.month and start_date.year == end_date.year:
            pdf_path = generate_quittance_pdf(tenant_name, start_date)
            with open(pdf_path, "rb") as pdf_file:
                update.message.reply_document(document=pdf_file)
            os.remove(pdf_path)
        else:
            filepaths = generate_quittances_pdf(tenant_name, start_date.strftime("%d/%m/%Y"), end_date.strftime("%d/%m/%Y"))

            zip_path = os.path.join("pdf/generated/", f"Quittances_{tenant_name.replace(' ', '_')}.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file in filepaths:
                    zipf.write(file, os.path.basename(file))
                    os.remove(file)

            with open(zip_path, "rb") as zip_file:
                update.message.reply_document(document=zip_file)
            os.remove(zip_path)

        update.message.reply_text(f"✅ Quittance générée avec succès pour {tenant_name}.")

    except Exception as e:
        print(f"❌ [DEBUG] Erreur lors de la génération : {str(e)}")
        update.message.reply_text(f"❌ Erreur : {str(e)}")
