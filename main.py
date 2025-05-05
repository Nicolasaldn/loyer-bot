import os
import requests

print("🚀 Test d’envoi Telegram simple")

# Récupération des variables d’environnement
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Vérifications
if not BOT_TOKEN or not CHAT_ID:
    print("❌ Variable d'environnement manquante : TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID")
    exit(1)

# Message à envoyer
message = "📢 Ceci est un message test envoyé automatiquement via le bot Telegram."

# Envoi
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

try:
    response = requests.post(url, data=payload)
    print("📤 Statut:", response.status_code)
    print("📬 Réponse:", response.text)
except Exception as e:
    print("❌ Erreur lors de l’envoi :", e)
