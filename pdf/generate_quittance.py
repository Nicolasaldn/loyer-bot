def generate_quittance_pdf(nom_locataire: str, date_obj, output_dir="pdf/generated"):
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%d/%m/%Y")

    infos = get_locataire_info(nom_locataire)
    mois_str = f"{FRENCH_MONTHS[date_obj.month]} {date_obj.year}"

    date_du_jour = datetime.now().strftime("%d/%m/%Y")
    date_debut = date_obj.replace(day=1)
    date_fin = (date_obj.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    bailleur_nom = infos.get("bailleur_nom", "Nom bailleur inconnu")
    bailleur_adresse = infos.get("bailleur_adresse", "")
    locataire_nom = infos.get("locataire_nom", "Nom locataire inconnu")
    locataire_adresse = infos.get("locataire_adresse", "Adresse inconnue")
    montant_loyer = infos.get("loyer_ttc", 0.00)
    date_paiement = infos.get("date_paiement", "Non précisée")

    pdf = QuittancePDF()
    pdf.add_page()

    # Titre principal
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "QUITTANCE DE LOYER", ln=True, align="C")
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 8, f"Période du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(10)

    # Coordonnées bailleur
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 6, f"{bailleur_nom}", ln=True)
    if bailleur_adresse:
        pdf.set_font("DejaVu", "", 11)
        pdf.multi_cell(0, 6, bailleur_adresse)
    pdf.ln(5)

    # Coordonnées locataire
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 6, f"Locataire : {locataire_nom}", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 6, locataire_adresse)
    pdf.ln(8)

    # Tableau de règlement
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 6, "DÉTAIL DU LOYER :", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(50, 6, "Loyer TTC :", ln=False)
    pdf.cell(0, 6, f"{montant_loyer:.2f} €", ln=True)
    pdf.cell(50, 6, "Date de paiement :", ln=False)
    pdf.cell(0, 6, date_paiement, ln=True)
    pdf.ln(10)

    # Déclaration
    texte = (
        f"Je soussigné(e) {bailleur_nom}, propriétaire du logement susmentionné, "
        f"atteste avoir reçu de {locataire_nom} la somme de {montant_loyer:.2f} € TTC "
        f"au titre du loyer pour la période indiquée ci-dessus. La présente quittance "
        f"vaut reçu définitif sous réserve de tous mes droits."
    )
    pdf.multi_cell(0, 6, texte)
    pdf.ln(10)

    # Signature
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 6, f"Fait à Paris, le {date_du_jour}", ln=True)
    pdf.ln(15)
    pdf.cell(0, 6, bailleur_nom, ln=True, align="R")

    # Génération du fichier
    os.makedirs(output_dir, exist_ok=True)
    filename = f"Quittance_{nom_locataire.replace(' ', '_')}_{mois_str.replace(' ', '_')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)

    return filepath
