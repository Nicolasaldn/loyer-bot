
import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

message = "📢 Ceci est un test automatique depuis Render et Google Sheets."

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, data=payload)
print("Message envoyé:", response.status_code, response.text)
