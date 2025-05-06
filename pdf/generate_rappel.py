from fpdf import FPDF
import os
from datetime import datetime, timedelta
from utils.sheets import get_locataire_info

FONT_PATH_REGULAR = "pdf/DejaVuSans.ttf"
FONT_PATH_BOLD = "pdf/DejaVuSans-Bold.ttf"
FONT_PATH_ITALIC = "pdf/DejaVuSans-Oblique.ttf"

class RappelPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("DejaVu", "", FONT_PATH_REGULAR, uni=True)
        self.add_font("DejaVu", "B", FONT_PATH_BOLD, uni=True)
        self.add_font("DejaVu", "I", FONT_PATH_ITALIC, uni=True)
        self.set_font("DejaVu", "", 10)

    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 8, "AVIS D'ÉCHÉANCE", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def get_periode(date: datetime, frequence: str) -> tuple:
    if frequence == "mensuel":
        start = date.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(days=1)
    elif frequence == "trimestriel":
        month = ((date.month - 1) // 3) * 3 + 1
        start = date.replace(month=month, day=1)
        next_quarter = month + 3
        year = date.year + (1 if next_quarter > 12 else 0)
        end_month = next_quarter if next_quarter <= 12 else next_quarter - 12
        end = datetime(year, end_month, 1) - timedelta(days=1)
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

    # Ligne période sous le titre
    pdf.set_font("DejaVu", "", 11)
    periode_txt = f"Avis d’échéance de loyer pour la période du {periode_debut.strftime('%d/%m/%Y')} au {periode_fin.strftime('%d/%m/%Y')}"
    pdf.cell(0, 8, periode_txt, ln=True, align="C")
    pdf.ln(8)

    # Bloc coordonnées (bailleur à gauche)
    pdf.set_font("DejaVu", "", 10)
    y_start = pdf.get_y()
    pdf.set_xy(15, y_start)
    pdf.multi_cell(80, 5, f"{infos['bailleur_nom']}\n{infos['bailleur_adresse']}")
    pdf.set_y(y_start)

    # Locataire à droite (collé bord droit)
    locataire_lines = f"{infos['locataire_nom']}\n{infos['locataire_adresse']}".split("\n")
    for line in locataire_lines:
        line_width = pdf.get_string_width(line)
        pdf.set_x(210 - 15 - line_width)
        pdf.cell(line_width, 5, line, ln=True)
    pdf.ln(8)

    # Fait à Paris
    pdf.set_x(15)
    pdf.cell(0, 6, f"Fait à Paris, le {date_du_jour}", ln=True)
    pdf.ln(10)

    # Adresse location
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 6, "ADRESSE DE LA LOCATION :", ln=True)
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 6, infos["locataire_adresse"], ln=True)
    pdf.ln(10)

    # Tableau
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(120, 8, "LIBELLÉ", border=1, fill=True)
    pdf.cell(0, 8, "MONTANT", border=1, ln=True, fill=True)

    pdf.set_font("DejaVu", "", 10)
    pdf.cell(120, 8, "Loyer TTC", border=1)
    pdf.cell(0, 8, f"{infos['loyer_ttc']:.2f} €", border=1, ln=True, align="R")

    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(120, 8, "TOTAL", border=1)
    pdf.cell(0, 8, f"{infos['loyer_ttc']:.2f} €", border=1, ln=True, align="R")
    pdf.ln(10)

    # Paiement exigible
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 8, f"PAIEMENT EXIGIBLE LE : {paiement_exigible}", ln=True)
    pdf.ln(6)

    # Texte bas de page
    pdf.set_font("DejaVu", "", 9.5)
    pdf.multi_cell(0, 6,
        "Le règlement est à effectuer par virement bancaire selon les modalités prévues dans le bail.\n"
        "En cas de difficulté, merci de me contacter dans les plus brefs délais."
    )

    # Sauvegarde
    os.makedirs(output_dir, exist_ok=True)
    filename = f"Avis_{nom_locataire.replace(' ', '_')}_{date.strftime('%Y-%m-%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath
