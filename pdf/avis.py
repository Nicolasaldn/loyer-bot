from fpdf import FPDF

class AvisLoyerPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "AVIS D'ÉCHÉANCE", ln=1, align="C")

    def generate(self, locataire, proprio_nom, proprio_adresse, date_rappel, frequence):
        nb_mois = 3 if frequence.lower().startswith("tri") else 1
        date_fin = date_rappel.replace(day=1).replace(month=((date_rappel.month - 1 + nb_mois) % 12 + 1))
        date_exigible = date_rappel.replace(day=1).replace(month=((date_rappel.month % 12) + 1))
        montant_total = locataire["loyer"] * nb_mois

        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Avis de loyer du {date_rappel.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}", ln=1, align="C")
        self.ln(5)

        self.set_font("Arial", "B", 11)
        self.cell(95, 8, "BAILLEUR :", ln=0)
        self.cell(95, 8, "LOCATAIRE :", ln=1)

        self.set_font("Arial", "", 11)
        self.cell(95, 6, proprio_nom, ln=0)
        self.cell(95, 6, locataire["nom"], ln=1)
        self.cell(95, 6, proprio_adresse, ln=0)
        self.cell(95, 6, locataire["adresse"], ln=1)
        self.ln(10)

        self.cell(0, 6, f"Fait à Paris, le {date_rappel.strftime('%d/%m/%Y')}", ln=1)
        self.ln(4)

        self.set_font("Arial", "B", 11)
        self.cell(0, 6, "ADRESSE DE LA LOCATION :", ln=1)
        self.set_font("Arial", "", 11)
        self.cell(0, 6, locataire["adresse"], ln=1)
        self.ln(6)

        self.set_fill_color(220, 220, 220)
        self.set_font("Arial", "B", 11)
        self.cell(90, 8, "LIBELLE", 1, 0, "L", 1)
        self.cell(50, 8, "MONTANT", 1, 1, "R", 1)

        self.set_font("Arial", "", 11)
        self.cell(90, 8, "Loyer TTC", 1, 0)
        self.cell(50, 8, f"{locataire['loyer']:.2f} EUR", 1, 1, "R")

        self.set_font("Arial", "B", 11)
        self.cell(90, 8, "Somme totale à régler", 1, 0)
        self.cell(50, 8, f"{montant_total:.2f} EUR", 1, 1, "R")
        self.ln(5)

        self.set_font("Arial", "", 11)
        self.cell(0, 6, f"PAIEMENT EXIGIBLE LE : {date_exigible.strftime('%d/%m/%Y')}", ln=1)
        self.ln(4)

        self.multi_cell(0, 6, "Cet avis est une demande de paiement. Il ne constitue pas une quittance.")

