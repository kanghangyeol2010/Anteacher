import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Use HF Inference API for efficiency
API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def analyze_sentiment(text):
    """
    Analyzes sentiment of text using Hugging Face Inference API.
    Returns a score between -1 and 1.
    """
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        result = response.json()
        
        # RoBERTa returns labels like 'positive', 'neutral', 'negative'
        # Format: [[{'label': 'positive', 'score': 0.9}, ...]]
        if isinstance(result, list) and len(result) > 0:
            scores = result[0]
            sentiment_map = {
                'positive': 1,
                'neutral': 0,
                'negative': -1
            }
            
            total_score = 0
            for s in scores:
                label = s['label'].lower()
                score = s['score']
                total_score += sentiment_map.get(label, 0) * score
            
            return total_score
        return 0
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return 0

def get_market_sentiment_index(news_list):
    """
    Calculates overall sentiment index from a list of news items.
    """
    if not news_list:
        return 0
    
    total_score = 0
    count = 0
    for item in news_list:
        title = item.get('title') or item.get('description') or ""
        if title:
            score = analyze_sentiment(title)
            total_score += score
            count += 1
    
    return total_score / count if count > 0 else 0
