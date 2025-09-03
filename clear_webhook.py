#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
if not bot_token:
    print("TELEGRAM_BOT_TOKEN not found")
    exit(1)

# Clear webhook
url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
response = requests.post(url)
print(f"Clear webhook: {response.json()}")

# Get bot info
url = f"https://api.telegram.org/bot{bot_token}/getMe"
response = requests.get(url)
print(f"Bot info: {response.json()}")