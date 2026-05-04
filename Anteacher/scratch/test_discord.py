import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_discord():
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not found in .env")
        return

    print(f"Testing Discord Webhook: {webhook_url[:20]}...")
    data = {
        "content": "🛠️ **[Anteacher Debug]** Webhook connection test successful!"
    }
    
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code in [200, 204]:
            print("✅ Discord Webhook Success!")
        else:
            print(f"❌ Discord Webhook Failure: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Discord Webhook Error: {e}")

if __name__ == "__main__":
    test_discord()
