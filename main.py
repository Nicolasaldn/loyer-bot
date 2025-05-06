import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from handlers.rappels import handle_rappel
from handlers.quittances import handle_quittance
from handlers.utils import parse_command

# Configure the logging module to output debug information
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Token for your Telegram bot
TOKEN = "YOUR_BOT_TOKEN"

# Initialize the bot
bot_app = Application.builder().token(TOKEN).build()

async def route_message(update: Update, context: CallbackContext):
    """Handle incoming messages and route based on command."""
    text = update.message.text.strip()  # Get the text of the message
    source, arguments = parse_command(text)  # Parse the command

    # Route based on the command source
    if source == "rappel":
        await handle_rappel(arguments, context)  # Handle the "rappel" command
    elif source == "quittance":
        await handle_quittance(arguments, context)  # Handle the "quittance" command
    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Commande non reconnue.")  # Unknown command

# Command handlers
async def start(update: Update, context: CallbackContext):
    """Send a welcome message when the user starts the bot."""
    await update.message.reply_text("Bonjour! Envoyez une commande pour commencer.")

def main():
    """Start the bot and set up the webhook."""
    bot_app.add_handler(CommandHandler("start", start))  # Add /start command handler
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))  # Route all text messages to route_message

    # Start the bot with webhook
    bot_app.run_polling()

if __name__ == "__main__":
    main()
