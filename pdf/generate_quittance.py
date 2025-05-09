from fpdf import FPDF
import os
from datetime import datetime, timedelta
from utils.sheets import get_locataire_info

FONT_PATH_REGULAR = "pdf/DejaVuSans.ttf"
FONT_PATH_BOLD = "pdf/DejaVuSans-Bold.ttf"
FONT_PATH_ITALIC = "pdf/DejaVuSans-Oblique.ttf"

FRENCH_MONTHS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril",
    5: "mai", 6: "juin", 7: "juillet", 8: "août",
    9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}

class QuittancePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("DejaVu", "", FONT_PATH_REGULAR, uni=True)
        self.add_font("DejaVu", "B", FONT_PATH_BOLD, uni=True)
        self.add_font("DejaVu", "I", FONT_PATH_ITALIC, uni=True)
        self.set_font("DejaVu", "", 10)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_quittance_pdf(nom_locataire: str, date_obj, output_dir="pdf/generated"):
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%d/%m/%Y")

    infos = get_locataire_info(nom_locataire)
    mois_str = f"{FRENCH_MONTHS[date_obj.month]} {date_obj.year}"

    date_du_jour = datetime.now().strftime("%d/%m/%Y")
    date_debut = date_obj.replace(day=1)
    date_fin = (date_obj.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    bailleur_nom = infos.get("bailleur_nom", "Nom bailleur inconnu")
    locataire_nom = infos.get("locataire_nom", "Nom locataire inconnu")
    montant_loyer = infos.get("loyer_ttc", 0.00)
    adresse_location = infos.get("locataire_adresse", "Adresse inconnue")
    date_paiement = infos.get("date_paiement", "Non précisée")

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
    pdf.multi_cell(0, 6, adresse_location)
    pdf.ln(4)

    # Paragraphe principal
    pdf.set_font("DejaVu", "", 11)
    texte = (
        f"Je soussigné(e) {bailleur_nom} propriétaire du logement désigné ci-dessus, déclare avoir reçu "
        f"de Mme {locataire_nom} la somme de {montant_loyer:.0f} euros ({montant_loyer:.0f} €), "
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
    pdf.cell(0, 6, f"{montant_loyer:.0f} euros", ln=True)
    pdf.cell(40, 6, "Date du paiement :", ln=False)
    pdf.cell(0, 6, date_paiement, ln=True)
    pdf.ln(10)

    # Date et signature
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 6, f"Fait le {date_du_jour}", ln=True)
    pdf.ln(10)
    pdf.cell(0, 6, bailleur_nom, ln=True, align="R")

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
