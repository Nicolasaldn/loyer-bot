import os
import json

print("🧪 Début du script de test")

try:
    raw_json = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")
    if not raw_json:
        raise ValueError("La variable GOOGLE_SHEET_CREDENTIALS_JSON est vide ou non définie.")
    
    print("🔍 Contenu brut détecté (début) :", raw_json[:60], "...")

    creds = json.loads(raw_json)
    print("✅ JSON chargé avec succès.")
    print("🔑 Type :", creds.get("type"))
    print("📧 Email du bot :", creds.get("client_email"))

except Exception as e:
    print("❌ Erreur au chargement du JSON :", e)
