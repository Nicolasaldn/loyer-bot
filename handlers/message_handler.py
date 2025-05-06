from telegram import Update
from telegram.ext import CallbackContext
from utils.sheets import list_tenants
from utils.state import set_user_state, get_user_state, clear_user_state

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    message_text = update.message.text.lower()

    # --- Cas 1 : l'utilisateur parle de "rappel"
    if "rappel" in message_text:
        set_user_state(user_id, {"action": "rappel"})
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="À quel locataire souhaites-tu envoyer un rappel ?"
        )
        return

    # --- Cas 2 : l'utilisateur a une action en cours (rappel)
    state = get_user_state(user_id)
    if state.get("action") == "rappel":
        tenants = [t.lower() for t in list_tenants()]
        found = next((t for t in tenants if t in message_text), None)

        if found:
            clear_user_state(user_id)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Ok, je vais générer un rappel pour {found.title()} 📬 (PDF à venir)"
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
