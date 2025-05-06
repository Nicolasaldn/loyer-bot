from telegram import Update, InputFile
from telegram.ext import ContextTypes
from utils.parser import parse_command
from utils.gsheet import get_worksheets
from pdf.avis_loyer import AvisLoyerPDF

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    text = update.message.text
    chat_id = update.message.chat_id
    command = parse_command(text)

    sheet_interface, sheet_db = get_worksheets()
    db_data = sheet_db.get_all_values()[1:]
    db_dict = {row[0]: row[1] for row in db_data}
    data = sheet_interface.get_all_values()[5:]

    if "error" in command:
        await context.bot.send_message(chat_id=chat_id, text="⛔ " + command["error"])
    elif command["type"] == "all":
        await context.bot.send_message(chat_id=chat_id, text=f"📄 Génération des rappels pour {command['date'].strftime('%d/%m/%Y')}...")
        for row in data:
            if len(row) >= 8 and row[7].strip().lower() == 'true':
                await generate_and_send_pdf(row, db_dict, command['date'], context, chat_id)
    elif command["type"] == "single":
        await context.bot.send_message(chat_id=chat_id, text=f"📄 Génération du rappel pour {command['nom']}...")
        for row in data:
            if row[1].strip().lower() == command['nom'].lower() and row[7].strip().lower() == 'true':
                await generate_and_send_pdf(row, db_dict, command['date'], context, chat_id)
                return
        await context.bot.send_message(chat_id=chat_id, text="❌ Locataire introuvable ou non à relancer.")

async def generate_and_send_pdf(row, db_dict, date_rappel, context, chat_id):
    locataire = {
        "nom": row[1].strip().title(),
        "adresse": row[3].strip(),
        "loyer": float(row[4])
    }
    proprio = row[6].strip()
    proprio_adresse = db_dict.get(proprio, "")
    frequence = row[5].strip()

    pdf = AvisLoyerPDF()
    pdf.add_page()
    pdf.generate(locataire, proprio, proprio_adresse, date_rappel, frequence)
    filename = f"/tmp/Avis_{locataire['nom'].replace(' ', '_')}_{date_rappel.strftime('%Y-%m-%d')}.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        await context.bot.send_document(chat_id=chat_id, document=InputFile(f), filename=filename.split("/")[-1])
