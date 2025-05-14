from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from utils.sheets import add_tenant, add_landlord
from utils.state import set_user_state, get_user_state, clear_user_state

# === États pour le ConversationHandler ===
ADD_TENANT_NAME, ADD_TENANT_EMAIL, ADD_TENANT_ADDRESS, ADD_TENANT_RENT, ADD_TENANT_FREQUENCY, ADD_TENANT_LANDLORD = range(6)
ADD_LANDLORD_NAME, ADD_LANDLORD_ADDRESS = range(2)

# === Gestion de l'ajout de locataire ===
def handle_add_tenant(update: Update, context: CallbackContext):
    message = update.message or update.callback_query.message
    message.reply_text("Quel est le nom du locataire ?")
    context.user_data['tenant_name'] = ""
    return ADD_TENANT_NAME

# === Gestion de l'ajout de bailleur ===
def handle_add_landlord(update: Update, context: CallbackContext):
    message = update.message or update.callback_query.message
    message.reply_text("Quel est le nom du bailleur ?")
    context.user_data['landlord_name'] = ""
    return ADD_LANDLORD_NAME

# === Étapes de locataire ===
def handle_add_tenant_name(update: Update, context: CallbackContext):
    context.user_data['tenant_name'] = update.message.text
    update.message.reply_text("Quel est l'email du locataire ?")
    return ADD_TENANT_EMAIL

def handle_add_tenant_email(update: Update, context: CallbackContext):
    context.user_data['tenant_email'] = update.message.text
    update.message.reply_text("Quelle est l'adresse du locataire ?")
    return ADD_TENANT_ADDRESS

def handle_add_tenant_address(update: Update, context: CallbackContext):
    context.user_data['tenant_address'] = update.message.text
    update.message.reply_text("Quel est le loyer TTC (€) ?")
    return ADD_TENANT_RENT

def handle_add_tenant_rent(update: Update, context: CallbackContext):
    context.user_data['tenant_rent'] = update.message.text
    update.message.reply_text("Quelle est la fréquence de paiement ?")
    return ADD_TENANT_FREQUENCY

def handle_add_tenant_frequency(update: Update, context: CallbackContext):
    context.user_data['tenant_frequency'] = update.message.text
    update.message.reply_text("Quel est le nom du propriétaire ?")
    return ADD_TENANT_LANDLORD

def handle_add_tenant_landlord(update: Update, context: CallbackContext):
    context.user_data['tenant_landlord'] = update.message.text

    add_tenant(
        context.user_data['tenant_name'],
        context.user_data['tenant_email'],
        context.user_data['tenant_address'],
        context.user_data['tenant_rent'],
        context.user_data['tenant_frequency'],
        context.user_data['tenant_landlord']
    )

    update.message.reply_text("✅ Locataire ajouté avec succès !")
    clear_user_state(update.effective_user.id)
    return ConversationHandler.END

# === Étapes de bailleur ===
def handle_add_landlord_name(update: Update, context: CallbackContext):
    context.user_data['landlord_name'] = update.message.text
    update.message.reply_text("Quelle est l'adresse du bailleur ?")
    return ADD_LANDLORD_ADDRESS

def handle_add_landlord_address(update: Update, context: CallbackContext):
    add_landlord(
        context.user_data['landlord_name'],
        update.message.text
    )

    update.message.reply_text("✅ Bailleur ajouté avec succès !")
    clear_user_state(update.effective_user.id)
    return ConversationHandler.END
