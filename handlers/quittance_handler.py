from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.sheets import list_tenants
from utils.state import set_user_state, clear_user_state, get_user_state
from pdf.generate_quittance import generate_quittance_pdf  # ✅ Utilisation correcte de la fonction
import os
import zipfile

def handle_quittance_command(update: Update, context: CallbackContext):
    tenants = list_tenants()
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"quittance:{name}")]
        for name in tenants
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Quel locataire pour la quittance ?",
        reply_markup=reply_markup
    )

def handle_quittance_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    if not data.startswith("quittance:"):
        return

    locataire = data.split(":", 1)[1].strip()
    user_id = update.effective_user.id

    set_user_state(user_id, {"action": "quittance", "name": locataire})

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Parfait, tu veux générer une quittance pour {locataire}.\n"
             "Indique la période (ex: janvier 2024 ou de janvier à mars 2024)."
    )

def handle_quittance_period(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    state = get_user_state(user_id)

    if state.get("action") == "quittance" and state.get("name"):
        locataire = state["name"]
        period = update.message.text.strip()

        try:
            # ✅ Détection de la période
            if "de" in period and "à" in period:
                start_month, end_month = map(str.strip, period.replace("de", "").split("à"))
                filepaths = generate_multiple_quittances(locataire, start_month, end_month)
                zip_path = create_zip_from_pdfs(filepaths, locataire, period)

                with open(zip_path, "rb") as zip_file:
                    context.bot.send_document(chat_id=update.effective_chat.id, document=zip_file)

                # Nettoyage
                for file in filepaths:
                    os.remove(file)
                os.remove(zip_path)

                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"✅ Quittances pour {locataire} générées avec succès pour la période {period}."
                )
            else:
                filepath = generate_quittance_pdf(locataire, period)  # ✅ Appel de la bonne fonction
                with open(filepath, "rb") as pdf_file:
                    context.bot.send_document(chat_id=update.effective_chat.id, document=pdf_file)
                os.remove(filepath)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"✅ Quittance pour {locataire} générée avec succès pour la période {period}."
                )
        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Erreur lors de la génération de la quittance : {str(e)}"
            )

        clear_user_state(user_id)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Une erreur s'est produite. Merci de recommencer avec /start."
        )

# ✅ Fonction pour gérer les quittances multiples (PDFs dans un ZIP)
def generate_multiple_quittances(locataire, start_month, end_month):
    from pdf.generate_quittance import generate_quittance_pdf  # ✅ Assure d'utiliser la bonne fonction
    filepaths = []

    # Liste des mois à générer (ici simplifié, à adapter si besoin)
    months = ["janvier", "février", "mars", "avril", "mai", "juin",
              "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    
    start_index = months.index(start_month.lower())
    end_index = months.index(end_month.lower()) + 1

    for month in months[start_index:end_index]:
        filepath = f"pdf/{locataire}_quittance_{month}.pdf"
        generate_quittance_pdf(locataire, month, filepath)
        filepaths.append(filepath)

    return filepaths

# ✅ Fonction pour créer un ZIP avec les quittances multiples
def create_zip_from_pdfs(filepaths, locataire, period):
    zip_filename = f"pdf/{locataire}_quittances_{period.replace(' ', '_')}.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for filepath in filepaths:
            zipf.write(filepath, os.path.basename(filepath))
    return zip_filename
