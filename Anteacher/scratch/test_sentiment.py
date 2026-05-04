import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def test_sentiment(text):
    print(f"Testing text: {text}")
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        print(f"Response Status: {response.status_code}")
        print(f"Response JSON: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sentiment("Hello, this is a great day!")
    test_sentiment("삼성전자 주가가 폭락하고 있습니다.") # Korean text
