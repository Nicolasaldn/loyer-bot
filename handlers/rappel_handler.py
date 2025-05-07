# rappel_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from pdf.generate_rappel import generate_rappel_pdf
import os

# ✅ Fonction principale pour lancer le rappel
def handle_rappel_command(update: Update, context: CallbackContext):
    tenants = ["Thomas Cohen", "Claire Dubois", "Jean Dujardin"]  # Tu peux remplacer par une liste dynamique.
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"rappel:{name}")]
        for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Quel locataire pour le rappel ?",
        reply_markup=reply_markup
    )

# ✅ Gestion de la sélection du locataire
def handle_rappel_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    if not data.startswith("rappel:"):
        return

    tenant_name = data.split(":", 1)[1].strip()
    context.user_data['rappel_tenant'] = tenant_name

    query.edit_message_text(
        f"Parfait, tu veux faire un rappel pour {tenant_name}.\nIndique la date souhaitée (JJ/MM/AAAA)."
    )

# ✅ Gestion de la réception de la date et génération du PDF
def handle_rappel_date(update: Update, context: CallbackContext):
    tenant_name = context.user_data.get('rappel_tenant')
    date = update.message.text.strip()

    if not tenant_name:
        update.message.reply_text("❌ Erreur : aucun locataire sélectionné.")
        return

    if not date:
        update.message.reply_text("❌ Erreur : aucune date fournie.")
        return
    
    try:
        # Montant par défaut (peut être rendu dynamique)
        montant = 500  # Remplace par la valeur correcte ou une variable dynamique

        # ✅ Génération du PDF
        pdf_path = f"pdf/{tenant_name}_rappel_{date.replace('/', '-')}.pdf"
        generate_rappel_pdf(tenant_name, date, montant, pdf_path)

        # ✅ Envoi du PDF
        with open(pdf_path, "rb") as pdf_file:
            context.bot.send_document(chat_id=update.message.chat_id, document=pdf_file)
        
        # ✅ Suppression du PDF après envoi
        os.remove(pdf_path)

        update.message.reply_text(
            f"✅ Rappel pour {tenant_name} généré avec succès pour la date {date}."
        )
    except Exception as e:
        update.message.reply_text(f"❌ Erreur lors de la génération du rappel : {str(e)}")
