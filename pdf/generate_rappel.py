from fpdf import FPDF
import os
from datetime import datetime, timedelta
from utils.sheets import get_locataire_info

FONT_PATH_REGULAR = "pdf/DejaVuSans.ttf"
FONT_PATH_BOLD = "pdf/DejaVuSans-Bold.ttf"
FONT_PATH_ITALIC = "pdf/DejaVuSans-Oblique.ttf"

class RappelPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu", "", FONT_PATH_REGULAR, uni=True)
        self.add_font("DejaVu", "B", FONT_PATH_BOLD, uni=True)
        self.add_font("DejaVu", "I", FONT_PATH_ITALIC, uni=True)
        self.set_font("DejaVu", "", 12)

    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 10, "Avis d'Echeance", ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def get_periode(date: datetime, frequence: str) -> tuple:
    if frequence == "mensuel":
        start = date.replace(day=1)
        next_month = start.replace(day=28) + timedelta(days=4)
        end = next_month - timedelta(days=next_month.day)
    elif frequence == "trimestriel":
        month = (date.month - 1) // 3 * 3 + 1
        start = date.replace(month=month, day=1)
        end_month = month + 2
        end = datetime(date.year, end_month, 1) + timedelta(days=32)
        end = end.replace(day=1) - timedelta(days=1)
    else:
        raise ValueError("Fréquence non supportée")
    return start, end

def generate_rappel_pdf(nom_locataire: str, date_str: str, output_dir="pdf/generated"):
    infos = get_locataire_info(nom_locataire)

    date = datetime.strptime(date_str, "%d/%m/%Y")
    periode_debut, periode_fin = get_periode(date, infos["frequence"])
    date_du_jour = datetime.now().strftime("%d/%m/%Y")
    paiement_exigible = (periode_fin + timedelta(days=1)).strftime("%d/%m/%Y")

    pdf = RappelPDF()
    pdf.add_page()

    # Coordonnées
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(100, 10, f"{infos['bailleur_nom']}", ln=0)
    pdf.cell(0, 10, f"Fait à Paris, le {date_du_jour}", ln=1)
    pdf.cell(100, 10, f"{infos['bailleur_adresse']}", ln=1)
    pdf.ln(10)

    pdf.cell(0, 10, f"À : {infos['locataire_nom']}", ln=1)
    pdf.cell(0, 10, f"{infos['locataire_adresse']}", ln=1)
    pdf.ln(10)

    # Objet
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Objet : Rappel - Avis d’échéance de loyer", ln=1)
    pdf.ln(5)

    # Corps
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 10,
        f"Je me permets de vous rappeler que le loyer de votre logement situé au {infos['locataire_adresse']} "
        f"pour la période du {periode_debut.strftime('%d/%m/%Y')} au {periode_fin.strftime('%d/%m/%Y')} "
        f"n’a pas encore été réglé à ce jour.\n\n"
        f"Le montant dû est de {infos['loyer_ttc']:.2f} € TTC, exigible au plus tard le {paiement_exigible}.\n\n"
        f"Merci de procéder au règlement dans les plus brefs délais.\n\n"
        f"Cordialement,\n{infos['bailleur_nom']}"
    )

    # Sauvegarde
    os.makedirs(output_dir, exist_ok=True)
    filename = f"Rappel_{nom_locataire.replace(' ', '_')}_{date.strftime('%Y-%m-%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)

    return filepath
