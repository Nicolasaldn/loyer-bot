from telegram import Update
from telegram.ext import CallbackContext
from utils.sheets import list_tenants
from utils.state import set_user_state, get_user_state, clear_user_state
from utils.parser import extract_name_and_date
from pdf.generate_rappel import generate_rappel_pdf

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    message_text = update.message.text.lower()

    # --- Cas 1 : intention de rappel détectée
    if "rappel" in message_text:
        set_user_state(user_id, {"action": "rappel"})
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="À quel locataire souhaites-tu envoyer un rappel ?"
        )
        return

    # --- Cas 2 : contexte actif (état = rappel)
    state = get_user_state(user_id)
    if state.get("action") == "rappel":
        name, date_str = extract_name_and_date(message_text)

        if name:
            clear_user_state(user_id)
            if date_str:
                filepath = generate_rappel_pdf(name, date_str)
                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=open(filepath, "rb")
                )
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Ok, je vais générer un rappel pour {name} 📬 (mais je n’ai pas reconnu de date)"
                )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Je n’ai pas reconnu ce locataire. Réessaie avec le nom exact."
            )
        return

    # --- Cas 3 : fallback
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Tape /start pour voir la liste des locataires."
    )
