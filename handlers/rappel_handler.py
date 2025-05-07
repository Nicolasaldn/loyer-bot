# rappel_handler.py

from pdf.generate_rappel import generate_rappel_pdf

def handle_rappel(update, context):
    query = update.callback_query
    query.answer()
    
    if query.data.startswith("rappel:"):
        tenant_name = query.data.split(":")[1]
        context.user_data['rappel_tenant'] = tenant_name
        query.edit_message_text(f"Parfait, tu veux faire un rappel pour {tenant_name}.\nIndique la date souhaitée (JJ/MM/AAAA).")
    else:
        # Recevoir la date du rappel
        tenant_name = context.user_data.get('rappel_tenant')
        date = update.message.text

        if not tenant_name:
            update.message.reply_text("Erreur : aucun locataire sélectionné.")
            return
        
        try:
            # Montant par défaut (à rendre dynamique plus tard)
            montant = 500  # Remplace par la valeur correcte ou une variable dynamique

            # Génération du PDF
            pdf_path = f"pdf/{tenant_name}_rappel_{date.replace('/', '-')}.pdf"
            generate_rappel_pdf(tenant_name, date, montant, pdf_path)

            # Envoi du PDF
            with open(pdf_path, "rb") as pdf_file:
                context.bot.send_document(chat_id=update.message.chat_id, document=pdf_file)
            
            # Suppression du PDF après envoi
            os.remove(pdf_path)
        except Exception as e:
            update.message.reply_text(f"❌ Erreur lors de la génération du rappel : {str(e)}")
