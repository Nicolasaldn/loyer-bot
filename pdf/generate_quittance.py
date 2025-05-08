from fpdf import FPDF
import os
from datetime import datetime, timedelta
from utils.sheets import get_locataire_info

FONT_PATH_REGULAR = "pdf/DejaVuSans.ttf"
FONT_PATH_BOLD = "pdf/DejaVuSans-Bold.ttf"
FONT_PATH_ITALIC = "pdf/DejaVuSans-Oblique.ttf"

class QuittancePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("DejaVu", "", FONT_PATH_REGULAR, uni=True)
        self.add_font("DejaVu", "B", FONT_PATH_BOLD, uni=True)
        self.add_font("DejaVu", "I", FONT_PATH_ITALIC, uni=True)
        self.set_font("DejaVu", "", 10)

    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 8, "QUITTANCE DE LOYER", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_quittance_pdf(nom_locataire: str, date_obj, output_dir="pdf/generated"):
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%d/%m/%Y")

    infos = get_locataire_info(nom_locataire)
    mois_str = date_obj.strftime("%B %Y")
    date_du_jour = datetime.now().strftime("%d/%m/%Y")

    pdf = QuittancePDF()
    pdf.add_page()

    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 8, f"Pour la période du {date_obj.strftime('%d/%m/%Y')} au {(date_obj.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1):%d/%m/%Y}", ln=True, align="C")

    y_start = pdf.get_y()
    pdf.set_xy(15, y_start)
    pdf.multi_cell(80, 5, f"{infos['bailleur_nom']}\n{infos['bailleur_adresse']}")

    pdf.ln(10)

    pdf.multi_cell(0, 6, f"Je soussigné {infos['bailleur_nom']}, déclare avoir reçu de {infos['locataire_nom']} la somme de {infos['loyer_ttc']:.2f} € TTC.")

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
