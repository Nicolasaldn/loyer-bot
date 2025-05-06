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
        self.cell(0, 10, "AVIS D'ÉCHÉANCE", ln=True, align="C")
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

    # --- Bloc coordonnées : bailleur gauche, locataire droite
    start_y = pdf.get_y()

    pdf.set_font("DejaVu", "", 10)
    pdf.set_xy(20, start_y)
    pdf.multi_cell(70, 5, f"{infos['bailleur_nom']}\n{infos['bailleur_adresse']}")

    pdf.set_xy(120, start_y)
    pdf.multi_cell(70, 5, f"{infos['locataire_nom']}\n{infos['locataire_adresse']}")
    pdf.ln(20)

    # --- Sous-titre centré : période
    pdf.set_font("DejaVu", "", 11)
    periode_txt = f"Avis d’échéance de loyer pour la période du {periode_debut.strftime('%d/%m/%Y')} au {periode_fin.strftime('%d/%m/%Y')}"
    pdf.multi_cell(0, 8, periode_txt, align="C")
    pdf.ln(5)

    # --- Fait à Paris
    pdf.set_font("DejaVu", "", 10)
    pdf.set_x(0)
    pdf.cell(0, 8, f"Fait à Paris, le {date_du_jour}", align="C", ln=True)
    pdf.ln(10)

    # --- Adresse du bien
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 7, "ADRESSE DE LA LOCATION :", ln=True)
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 6, infos["locataire_adresse"])
    pdf.ln(10)

    # --- Tableau
    col1_width = 100
    col2_width = 80
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(col1_width, 10, "LIBELLÉ", border=1, fill=True)
    pdf.cell(col2_width, 10, "MONTANT", border=1, ln=True, fill=True)

    pdf.set_font("DejaVu", "", 10)
    pdf.cell(col1_width, 10, "Loyer TTC", border=1)
    pdf.cell(col2_width, 10, f"{infos['loyer_ttc']:.2f} €".rjust(15), border=1, ln=True)

    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(col1_width, 10, "TOTAL", border=1)
    pdf.cell(col2_width, 10, f"{infos['loyer_ttc']:.2f} €".rjust(15), border=1, ln=True)
    pdf.ln(10)

    # --- Paiement exigible
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 10, f"PAIEMENT EXIGIBLE LE : {paiement_exigible}", ln=True)
    pdf.ln(6)

    # --- Texte final
    pdf.set_font("DejaVu", "", 9.5)
    pdf.multi_cell(0, 6,
        "Le règlement est à effectuer par virement bancaire selon les modalités prévues dans le bail.\n"
        "En cas de difficulté, merci de me contacter dans les plus brefs délais."
    )

    # --- Export
    os.makedirs(output_dir, exist_ok=True)
    filename = f"Avis_{nom_locataire.replace(' ', '_')}_{date.strftime('%Y-%m-%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)

    return filepath
