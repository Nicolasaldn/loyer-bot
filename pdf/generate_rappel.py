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
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("DejaVu", "", FONT_PATH_REGULAR, uni=True)
        self.add_font("DejaVu", "B", FONT_PATH_BOLD, uni=True)
        self.add_font("DejaVu", "I", FONT_PATH_ITALIC, uni=True)
        self.set_font("DejaVu", "", 12)

    def header(self):
        self.set_font("DejaVu", "B", 16)
        self.cell(0, 10, "AVIS D'ÉCHÉANCE", ln=True, align="C")
        self.set_font("DejaVu", "", 12)
        self.ln(2)

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

    # --- Coordonnées haut de page : Bailleur à gauche, Locataire à droite
    pdf.set_font("DejaVu", "", 12)
    top_y = pdf.get_y()

    # Bailleur (gauche)
    pdf.set_xy(15, top_y)
    pdf.multi_cell(80, 6, f"{infos['bailleur_nom']}\n{infos['bailleur_adresse']}")

    # Locataire (droite)
    pdf.set_xy(115, top_y)
    pdf.multi_cell(80, 6, f"{infos['locataire_nom']}\n{infos['locataire_adresse']}")

    pdf.ln(15)

    # Période
    pdf.set_font("DejaVu", "", 12)
    periode_txt = f"Avis d’échéance de loyer pour la période du {periode_debut.strftime('%d/%m/%Y')} au {periode_fin.strftime('%d/%m/%Y')}"
    pdf.multi_cell(0, 8, periode_txt, align="C")
    pdf.ln(10)

    # Fait à Paris
    pdf.set_x(15)
    pdf.cell(0, 8, f"Fait à Paris, le {date_du_jour}", ln=True)
    pdf.ln(5)

    # Adresse du bien
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "ADRESSE DE LA LOCATION :", ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 8, infos["locataire_adresse"])
    pdf.ln(10)

    # Tableau : Libellé / Montant
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(95, 10, "LIBELLÉ", border=1)
    pdf.cell(0, 10, "MONTANT", border=1, ln=True)

    pdf.set_font("DejaVu", "", 12)
    pdf.cell(95, 10, "Loyer TTC", border=1)
    pdf.cell(0, 10, f"{infos['loyer_ttc']:.2f} €", border=1, ln=True)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(95, 10, "TOTAL", border=1)
    pdf.cell(0, 10, f"{infos['loyer_ttc']:.2f} €", border=1, ln=True)
    pdf.ln(10)

    # Paiement exigible
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, f"PAIEMENT EXIGIBLE LE : {paiement_exigible}", ln=True)
    pdf.ln(8)

    # Texte final
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 7,
        "Le règlement est à effectuer par virement bancaire selon les modalités prévues dans le bail.\n"
        "En cas de difficulté, merci de me contacter dans les plus brefs délais."
    )

    # Sauvegarde
    os.makedirs(output_dir, exist_ok=True)
    filename = f"Avis_{nom_locataire.replace(' ', '_')}_{date.strftime('%Y-%m-%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)

    return filepath
