import FinanceDataReader as fdr
import pandas as pd
import streamlit as st
from core.data_fetcher import fetch_stock_data
from core.calculus import calculate_derivatives
from core.sentiment import get_market_sentiment_index
from core.data_fetcher import fetch_news_rss

@st.cache_data(ttl=3600)  # 1시간 캐싱
def get_anteacher_recommendations(limit=3):
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
            
            # 최근 1개월 데이터
            df = fetch_stock_data(code, period='1mo')
            if df is not None and len(df) > 5:
                df = calculate_derivatives(df)
                latest_slope = df['Slope'].iloc[-1]
                latest_acc = df['Acceleration'].iloc[-1]
                latest_close = df['Close'].iloc[-1]
                
                # 뉴스 감성 점수 (간단하게 3개만)
                news = fetch_news_rss(name)
                sentiment = get_market_sentiment_index(news)
                
                # ── 상승 확률 계산 (Sigmoid 정규화)
                # 기울기, 가속도, 심리점수를 가중치 있게 합산
                import numpy as np
                score = (latest_slope * 0.5) + (latest_acc * 0.3) + (sentiment * 0.2)
                # sigmoid: 1 / (1 + exp(-k * score))
                prob = 1 / (1 + np.exp(-5.0 * score))
                
                # ── 확률 보정 (현실화)
                # 100%는 없으므로 최대 95%로 제한(Cap)
                final_prob = min(int(prob * 100), 95)
                # 하한선 설정 (범위 표현용: 보통 10~15% 정도의 오차 범위)
                rise_prob_low = max(final_prob - 15, 5)
                
                # Market 구분
                market = "KRX" if code.isdigit() else "US"
                
                results.append({
                    'code': code,
                    'name': name,
                    'slope': latest_slope,
                    'acc': latest_acc,
                    'close': latest_close,
                    'sentiment': sentiment,
                    'rise_prob': final_prob,
                    'rise_prob_low': rise_prob_low,
                    'market': market,
                    'df': df
                })
        
        # 상승 확률 기준 내림차순 정렬
        sorted_results = sorted(results, key=lambda x: x['rise_prob'], reverse=True)
        return sorted_results[:limit]
    except Exception as e:
        print(f"추천 시스템 오류: {e}")
        return []
