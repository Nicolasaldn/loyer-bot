from telegram import Update
from telegram.ext import ContextTypes

async def handle_quittance(update: Update, context: ContextTypes.DEFAULT_TYPE, *args):
    await update.message.reply_text("📄 Fonction quittance pas encore implémentée.")
