def generate_quittance_pdf(nom_locataire: str, date_obj, output_dir="pdf/generated"):
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%d/%m/%Y")

    infos = get_locataire_info(nom_locataire)
    mois_str = date_obj.strftime("%B %Y")
    date_du_jour = datetime.now().strftime("%d/%m/%Y")
    date_debut = date_obj.replace(day=1)
    date_fin = (date_obj.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    pdf = QuittancePDF()
    pdf.add_page()

    # Titre
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, "Quittance de loyer", ln=True, align="C")
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 8, mois_str, ln=True, align="C")
    pdf.ln(5)

    # Adresse de la location
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 6, "Adresse de la location :", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 6, infos["adresse_location"])
    pdf.ln(4)

    # Paragraphe principal
    pdf.set_font("DejaVu", "", 11)
    texte = (
        f"Je soussigné(e) {infos['bailleur_nom']} propriétaire du logement désigné ci-dessus, déclare avoir reçu "
        f"de Mme {infos['locataire_nom']} la somme de {infos['loyer_ttc']:.0f} euros ({infos['loyer_ttc']:.0f} €), "
        f"au titre du paiement du loyer et des charges pour la période de location du {date_debut.strftime('%d/%m/%Y')} "
        f"au {date_fin.strftime('%d/%m/%Y')} et lui en donne quittance, sous réserve de tous mes droits."
    )
    pdf.multi_cell(0, 6, texte)
    pdf.ln(5)

    # Détail du règlement
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 6, "Détail du règlement :", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(40, 6, "Loyer :", ln=False)
    pdf.cell(0, 6, f"{infos['loyer_ttc']:.0f} euros", ln=True)
    pdf.cell(40, 6, "Date du paiement :", ln=False)
    pdf.cell(0, 6, infos["date_paiement"], ln=True)
    pdf.ln(10)

    # Date et signature
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 6, f"Fait le {date_du_jour}", ln=True)
    pdf.ln(10)
    pdf.cell(0, 6, infos["bailleur_nom"], ln=True, align="R")

    # Génération du fichier
    os.makedirs(output_dir, exist_ok=True)
    filename = f"Quittance_{nom_locataire.replace(' ', '_')}_{mois_str.replace(' ', '_')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)

    return filepath
def generate_quittances_pdf(nom_locataire: str, date_debut: str, date_fin: str) -> list:
    start = datetime.strptime(date_debut, "%d/%m/%Y")
    end = datetime.strptime(date_fin, "%d/%m/%Y")
    fichiers = []

    current = start
    while current <= end:
        filepath = generate_quittance_pdf(nom_locataire, current)
        fichiers.append(filepath)
        current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)

    return fichiers
