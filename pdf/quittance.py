from fpdf import FPDF

class QuittancePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "QUITTANCE DE LOYER", ln=1, align="C")

    def generate(self, locataire, proprio_nom, proprio_adresse, date_debut, date_fin, montant, mois_texte):
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Quittance pour la période du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}", ln=1, align="C")
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

        self.multi_cell(0, 6, f"Je soussigné {proprio_nom}, reconnais avoir reçu de {locataire['nom']} la somme de {montant} € au titre du paiement du loyer pour la période indiquée ci-dessus.", align="J")
        self.ln(10)
        self.cell(0, 6, f"Fait à Paris, le {date_fin.strftime('%d/%m/%Y')}", ln=1)
