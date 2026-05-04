import requests
import os
from dotenv import load_dotenv
from core.ai_orchestrator import get_gemini_sentiment

load_dotenv()

# Use HF Inference API for global news (RoBERTa model)
API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def analyze_sentiment_hf(text):
    """
    Analyzes sentiment of English text using Hugging Face Inference API.
    Returns a score between -1 and 1.
    """
    if not text:
        return 0.0
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=5)
        if response.status_code != 200:
             return 0.0
             
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            scores = result[0]
            # RoBERTa labels: 'positive', 'neutral', 'negative'
            sentiment_map = {'positive': 1.0, 'neutral': 0.0, 'negative': -1.0}
            total_score = 0.0
            for s in scores:
                label = s['label'].lower()
                score = s['score']
                total_score += sentiment_map.get(label, 0) * score
            return total_score
        return 0.0
    except:
        return 0.0

def get_market_sentiment_index(local_news, global_news=None):
    """
    Calculates combined sentiment index.
    - Local News (Korean): Analyzed via Gemini
    - Global News (English): Analyzed via Hugging Face (RoBERTa)
    """
    local_score = 0.0
    has_local = False
    if local_news:
        local_score = get_gemini_sentiment(local_news)
        has_local = True
    
    global_score = 0.0
    has_global = False
    if global_news and len(global_news) > 0:
        hf_scores = []
        for item in global_news:
            title = item.get('title') or item.get('description') or ""
            if title:
                s = analyze_sentiment_hf(title)
                hf_scores.append(s)
        
        if hf_scores:
            # Check if HF actually returned something other than absolute zero (model loading/failure)
            global_score = sum(hf_scores) / len(hf_scores)
            has_global = any(s != 0.0 for s in hf_scores)
    
    # ── Weighted average logic ──
    # If global analysis returned absolute neutral (0.0), it likely failed or is loading.
    # In that case, we trust the local (Gemini) score more.
    if has_local and has_global:
        return (local_score * 0.6) + (global_score * 0.4)
    elif has_local:
        return local_score
    elif has_global:
        return global_score
    else:
        return 0.0
