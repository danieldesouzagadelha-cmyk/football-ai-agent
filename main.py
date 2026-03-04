import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("TOKEN:", TOKEN)
print("CHAT_ID:", CHAT_ID)

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": "🚀 TESTE FINAL AGORA"
}

response = requests.post(url, data=payload)

print("STATUS:", response.status_code)
print("RESPOSTA:", response.text)
