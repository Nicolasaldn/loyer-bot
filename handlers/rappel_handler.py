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

    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )
    print("✅ [DEBUG] Commande rappel déclenchée.")
    return SELECT_TENANT

def handle_rappel_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    try:
        tenant_name = query.data.split(":", 1)[1].strip()
    except IndexError:
        print("❌ [DEBUG] Erreur : Nom de locataire introuvable dans le callback data.")
        query.edit_message_text("❌ Erreur : Le locataire sélectionné est invalide.")
        return ConversationHandler.END

    context.user_data['rappel_tenant'] = tenant_name
    print(f"✅ [DEBUG] Locataire sélectionné : {tenant_name}")

    query.edit_message_text(
        f"Parfait, tu veux faire un rappel pour {tenant_name}.\nIndique la date souhaitée (JJ/MM/AAAA)."
    )
    return ENTER_DATE

def handle_rappel_date(update: Update, context: CallbackContext):
    tenant_name = context.user_data.get('rappel_tenant')
    date = update.message.text.strip()
    print(f"✅ [DEBUG] Date reçue : {date} pour {tenant_name}")

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné.")
        print("❌ [DEBUG] Aucun locataire sélectionné.")
        return ConversationHandler.END

    if not date:
        update.message.reply_text("❌ Erreur : aucune date fournie.")
        print("❌ [DEBUG] Date non fournie.")
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
        pdf_filename = f"Avis_{tenant_name.replace(' ', '_')}_{date.replace('/', '-')}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        print(f"✅ [DEBUG] Chemin cible du PDF : {pdf_path}")

        # ✅ Génération du PDF
        generated_pdf_path = generate_rappel_pdf(tenant_name, date, output_dir=output_dir)
        print(f"✅ [DEBUG] PDF généré à : {generated_pdf_path}")

        # ✅ Vérification de l'existence du PDF avant envoi
        if not os.path.exists(generated_pdf_path):
            print(f"❌ [DEBUG] Le fichier PDF n'a pas été généré.")
            update.message.reply_text("❌ Erreur : Le PDF n'a pas pu être généré.")
            return ConversationHandler.END

        # ✅ Envoi du PDF
        with open(generated_pdf_path, "rb") as pdf_file:
            update.message.reply_document(document=pdf_file)
            print(f"✅ [DEBUG] PDF envoyé : {generated_pdf_path}")
        
        # ✅ Suppression du PDF après envoi
        os.remove(generated_pdf_path)
        print(f"✅ [DEBUG] PDF supprimé : {generated_pdf_path}")

        update.message.reply_text(
            f"✅ Rappel pour {tenant_name} généré avec succès pour la date {date}."
        )
        return ConversationHandler.END

    except Exception as e:
        print(f"❌ [DEBUG] Erreur lors de la génération du rappel : {str(e)}")
        update.message.reply_text(f"❌ Erreur lors de la génération du rappel : {str(e)}")
        return ConversationHandler.END
