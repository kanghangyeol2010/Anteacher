import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests

load_dotenv()

def test_gemini():
    print("Testing Gemini API...")
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content("Hello")
        print(f"Gemini Success: {response.text}")
    except Exception as e:
        print(f"Gemini Failure: {e}")

def test_fred():
    print("Testing FRED API...")
    api_key = os.getenv('FRED_API_KEY')
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={api_key}&file_type=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("FRED Success")
        else:
            print(f"FRED Failure: {response.status_code}")
    except Exception as e:
        print(f"FRED Error: {e}")

if __name__ == "__main__":
    test_gemini()
    test_fred()
