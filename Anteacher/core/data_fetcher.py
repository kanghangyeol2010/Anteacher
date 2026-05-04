import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import requests
import feedparser
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_stock_data(symbol, period='1y'):
    """
    Fetches stock data using yfinance. 
    If it looks like a KRX stock (e.g., '005930'), try FinanceDataReader.
    """
    try:
        if symbol.isdigit() and len(symbol) == 6:
            # Likely Korean stock
            df = fdr.DataReader(symbol)
            # FDR might use lowercase or different names depending on version/source
            df.columns = [c.capitalize() for c in df.columns]
            return df
        else:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            return df
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

def fetch_fred_data(series_id='DGS10'):
    """
    Fetches macro data from FRED.
    DGS10: Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity
    """
    api_key = os.getenv('FRED_API_KEY')
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    
    try:
        response = requests.get(url)
        data = response.json()
        observations = data['observations']
        df = pd.DataFrame(observations)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df.set_index('date', inplace=True)
        return df[['value']]
    except Exception as e:
        print(f"Error fetching FRED data: {e}")
        return None

def fetch_news_rss(query):
    """
    Fetches news from Google News RSS.
    """
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    news_items = []
    for entry in feed.entries[:10]:
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published
        })
    return news_items

def fetch_naver_news(query):
    client_id = os.getenv('NAVER_CLIENT_ID')
    client_secret = os.getenv('NAVER_CLIENT_SECRET')
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=10&sort=sim"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json().get('items', [])
    except:
        return []

def fetch_global_news(query):
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&pageSize=10"
    try:
        response = requests.get(url)
        return response.json().get('articles', [])
    except:
        return []

def fetch_financial_metrics(symbol):
    """
    Fetches key financial metrics (PER, PBR, ROE) using yfinance.
    """
    try:
        yf_symbol = symbol
        # Handle Korean stocks for yfinance (6-digit code)
        if symbol.isdigit() and len(symbol) == 6:
            # Try KOSPI (.KS) first
            yf_symbol = symbol + ".KS"
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            # If no info or fundamental data, try KOSDAQ (.KQ)
            if not info or 'regularMarketPrice' not in info or 'trailingPE' not in info:
                yf_symbol = symbol + ".KQ"
                ticker = yf.Ticker(yf_symbol)
                info = ticker.info
        else:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info

        # Extract metrics with fallbacks
        metrics = {
            'per': info.get('trailingPE') or info.get('forwardPE'),
            'pbr': info.get('priceToBook'),
            'roe': info.get('returnOnEquity'),
            'eps': info.get('trailingEps'),
            'bps': info.get('bookValue'),
            'market_price': info.get('regularMarketPrice') or info.get('currentPrice'),
            'dividendYield': info.get('dividendYield'),
            'netIncomeToCommon': info.get('netIncomeToCommon'),
            'totalRevenue': info.get('totalRevenue')
        }
        
        # Calculate ROE manually if missing but net income and equity are available
        # yfinance often lacks 'returnOnEquity' for KR stocks
        if metrics['roe'] is None and metrics['netIncomeToCommon'] is not None:
             # Total Equity = Total Assets - Total Liabilities (but we might not have it in info)
             # Let's try to get it from balance sheet if needed, but info is faster.
             pass

        return metrics
    except Exception as e:
        print(f"Error fetching financial metrics for {symbol}: {e}")
        return None
