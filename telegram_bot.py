import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")   # ← mudou aqui

def send_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    response = requests.post(url, data=payload)

    print("STATUS:", response.status_code)
    print("RESPOSTA:", response.text)
