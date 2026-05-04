import FinanceDataReader as fdr
import pandas as pd
import streamlit as st
from core.data_fetcher import fetch_stock_data
from core.calculus import calculate_derivatives
from core.sentiment import get_market_sentiment_index
from core.data_fetcher import fetch_news_rss

@st.cache_data(ttl=3600)  # 1시간 캐싱
def get_anteacher_recommendations(limit=3, cache_bust="v2"):
    """
    시가총액 상위 종목 중 최근 기울기가 가장 가파른 3종목 선정
    """
    try:
        # KOSPI 상위 20개 종목 리스트 (간소화를 위해 20개 중 선정)
        df_kospi = fdr.StockListing('KOSPI')
        top_picks = df_kospi.head(15)  # 상위 15개만 검사
        
        results = []
        for _, row in top_picks.iterrows():
            code = row['Code']
            name = row['Name']
            
            df = fetch_stock_data(code, period='1mo')
            if df is not None and len(df) > 5:
                df = calculate_derivatives(df)
                latest_slope = df['Slope'].iloc[-1]
                latest_acc = df['Acceleration'].iloc[-1]
                latest_close = df['Close'].iloc[-1]
                
                # 기술적 지표만으로 우선 점수 계산 (API 호출 X)
                tech_score = (latest_slope * 0.7) + (latest_acc * 0.3)
                
                results.append({
                    'code': code,
                    'name': name,
                    'slope': latest_slope,
                    'acc': latest_acc,
                    'close': latest_close,
                    'tech_score': tech_score,
                    'df': df
                })
        
        # 기술적 지표 상위 5개만 정밀 분석 (API 호출 최소화)
        candidates = sorted(results, key=lambda x: x['tech_score'], reverse=True)[:5]
        
        # 1. Fetch news for all candidates
        for item in candidates:
            item['news'] = fetch_news_rss(item['name'])
            
        # 2. Batch AI Analysis (Single API Call)
        from core.ai_orchestrator import get_batch_sentiment_and_reason
        batch_results = get_batch_sentiment_and_reason(candidates)
        if not batch_results:
            batch_results = {item['code']: {"sentiment": 0.0, "reason": "AI 한도 초과로 쉬는 중 ⏳"} for item in candidates}
        
        final_picks = []
        import numpy as np
        
        # 3. Calculate final scores
        for item in candidates:
            ticker = item['code']
            ai_data = batch_results.get(ticker, {})
            sentiment = float(ai_data.get('sentiment', 0.0))
            reason = ai_data.get('reason', '분석 중 오류가 발생했습니다. 🧐')
            
            score = (item['slope'] * 0.5) + (item['acc'] * 0.3) + (sentiment * 0.2)
            prob = 1 / (1 + np.exp(-5.0 * score))
            final_prob = min(int(prob * 100), 95)
            rise_prob_low = max(final_prob - 15, 5)
            
            item['sentiment'] = sentiment
            item['reason'] = reason
            item['rise_prob'] = final_prob
            item['rise_prob_low'] = rise_prob_low
            item['market'] = "KRX" if item['code'].isdigit() else "US"
            final_picks.append(item)
            
        return sorted(final_picks, key=lambda x: x['rise_prob'], reverse=True)[:limit]
    except Exception as e:
        print(f"추천 시스템 오류: {e}")
        return []
