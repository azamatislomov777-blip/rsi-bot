import os
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

print("🚀 Bot started")

send_message("✅ RSI Bot успешно запущен на Railway!")

while True:
    print("Bot is running...")
    time.sleep(1200)  # 20 минут
