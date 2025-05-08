# rappel_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import os

# ✅ Import sécurisé de la fonction generate_rappel_pdf
try:
    from pdf.generate_rappel import generate_rappel_pdf
except ImportError:
    print("❌ [DEBUG] Erreur : La fonction generate_rappel_pdf n'a pas été trouvée.")
    generate_rappel_pdf = None

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
    print("✅ [DEBUG] Commande rappel déclenchée.")
    return SELECT_TENANT

def handle_rappel_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    tenant_name = query.data.split(":", 1).strip()
    context.user_data['rappel_tenant'] = tenant_name

    query.edit_message_text(
        f"Parfait, tu veux faire un rappel pour {tenant_name}.\nIndique la date souhaitée (JJ/MM/AAAA)."
    )
    print(f"✅ [DEBUG] Locataire sélectionné : {tenant_name}")
    return ENTER_DATE

def handle_rappel_date(update: Update, context: CallbackContext):
    tenant_name = context.user_data.get('rappel_tenant')
    date = update.message.text.strip()
    print(f"✅ [DEBUG] Date reçue : {date} pour {tenant_name}")

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné.")
        return ConversationHandler.END

    if not date:
        update.message.reply_text("❌ Erreur : aucune date fournie.")
        return ENTER_DATE

    if not generate_rappel_pdf:
        update.message.reply_text("❌ Erreur : La fonction de génération de rappel n'est pas disponible.")
        print("❌ [DEBUG] La fonction generate_rappel_pdf n'est pas définie.")
        return ConversationHandler.END

    try:
        # ✅ Assure que le dossier pdf/generated/ existe
        output_dir = "pdf/generated/"
        os.makedirs(output_dir, exist_ok=True)
        
        # ✅ Génération du PDF avec chemin sécurisé
        pdf_path = os.path.join(output_dir, f"Avis_{tenant_name.replace(' ', '_')}_{date.replace('/', '-')}.pdf")
        print(f"✅ [DEBUG] Génération du PDF à : {pdf_path}")
        generate_rappel_pdf(tenant_name, date, output_dir=output_dir)

        # ✅ Vérification de l'existence du PDF avant envoi
        if not os.path.exists(pdf_path):
            print(f"❌ [DEBUG] Le fichier PDF n'a pas été généré.")
            update.message.reply_text("❌ Erreur : Le PDF n'a pas pu être généré.")
            return ConversationHandler.END

        # ✅ Envoi du PDF
        with open(pdf_path, "rb") as pdf_file:
            update.message.reply_document(document=pdf_file)
            print(f"✅ [DEBUG] PDF envoyé : {pdf_path}")
        
        # ✅ Suppression du PDF après envoi
        os.remove(pdf_path)
        print(f"✅ [DEBUG] PDF supprimé : {pdf_path}")

        update.message.reply_text(
            f"✅ Rappel pour {tenant_name} généré avec succès pour la date {date}."
        )
        return ConversationHandler.END

    except Exception as e:
        print(f"❌ [DEBUG] Erreur lors de la génération du rappel : {str(e)}")
        update.message.reply_text(f"❌ Erreur lors de la génération du rappel : {str(e)}")
        return ConversationHandler.END
