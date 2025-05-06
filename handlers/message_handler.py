from utils.parser import extract_name_and_date
from pdf.generate_rappel import generate_rappel_pdf
from utils.state import set_user_state, get_user_state, clear_user_state, update_user_state
from utils.sheets import list_tenants
from telegram import Update
from telegram.ext import CallbackContext

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    message_text = update.message.text.lower()

    # Toujours essayer d’extraire nom + date
    name, date_str = extract_name_and_date(message_text)
    state = get_user_state(user_id)

    # Cas 1 — message contient tout : nom + date → on agit immédiatement
    if name and date_str:
        clear_user_state(user_id)
        filepath = generate_rappel_pdf(name, date_str)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
        return

    # Cas 2 — message contient le mot "rappel" → activer le contexte
    if "rappel" in message_text:
        set_user_state(user_id, {"action": "rappel"})
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="À quel locataire souhaites-tu envoyer un rappel ?"
        )
        return

    # Cas 3 — contexte actif + nom trouvé → on attend la date
    if state.get("action") == "rappel" and name:
        update_user_state(user_id, "name", name)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Parfait, tu veux faire un rappel pour {name.title()}. Donne-moi maintenant la date (JJ/MM/AAAA)."
        )
        return

    # Cas 4 — contexte actif + date uniquement + nom déjà stocké
    if state.get("action") == "rappel" and date_str and state.get("name"):
        name = state["name"]
        clear_user_state(user_id)
        filepath = generate_rappel_pdf(name, date_str)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, "rb"))
        return

    # Cas fallback
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Tape /start pour voir la liste des locataires."
    )
