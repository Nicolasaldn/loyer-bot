# pdf/generate_rappel.py

from fpdf import FPDF
import os

class RappelPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Avis de Rappel de Paiement", ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_rappel_pdf(nom_locataire: str, mois: str, montant: float = 800.0, output_dir="pdf/generated"):
    pdf = RappelPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 12)

    # Corps du message
    pdf.ln(10)
    pdf.multi_cell(0, 10, 
        f"Bonjour {nom_locataire},\n\n"
        f"Nous vous rappelons que le loyer du mois de {mois} d’un montant de {montant:.2f} € reste à régler.\n"
        f"Merci de procéder au paiement dans les plus brefs délais.\n\n"
        f"Cordialement,\nVotre gestionnaire de biens"
    )

    # Création du dossier si nécessaire
    os.makedirs(output_dir, exist_ok=True)

    # Nom du fichier
    filename = f"{nom_locataire.replace(' ', '_')}_{mois.replace(' ', '_')}.pdf"
    filepath = os.path.join(output_dir, filename)

    pdf.output(filepath)
    return filepath
