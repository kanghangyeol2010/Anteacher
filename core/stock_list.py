import pandas as pd
import streamlit as st

@st.cache_data(ttl=86400, show_spinner=False)  # 하루 1회 캐싱
def load_stock_universe():
    """
    KOSPI, KOSDAQ, S&P500, NASDAQ 종목 리스트를 불러와 통합 DataFrame 반환.
    Columns: name, code, market, search_key
    """
    import FinanceDataReader as fdr

    frames = []

    # ── 한국 시장
    for market in ('KOSPI', 'KOSDAQ'):
        try:
            df = fdr.StockListing(market)[['Code', 'Name']].copy()
            df.columns = ['code', 'name']
            df['market'] = market
            frames.append(df)
        except Exception as e:
            print(f"[StockList] {market} 로딩 실패: {e}")

    # ── 미국 시장
    for market in ('S&P500', 'NASDAQ'):
        try:
            df = fdr.StockListing(market)[['Symbol', 'Name']].copy()
            df.columns = ['code', 'name']
            df['market'] = market
            frames.append(df)
        except Exception as e:
            print(f"[StockList] {market} 로딩 실패: {e}")

    if not frames:
        # 폴백: 기본 종목 하드코딩
        fallback = [
            {'code': '005930', 'name': '삼성전자',       'market': 'KOSPI'},
            {'code': '000660', 'name': 'SK하이닉스',      'market': 'KOSPI'},
            {'code': '035420', 'name': 'NAVER',           'market': 'KOSPI'},
            {'code': 'AAPL',   'name': 'Apple',           'market': 'NASDAQ'},
            {'code': 'MSFT',   'name': 'Microsoft',       'market': 'NASDAQ'},
            {'code': 'NVDA',   'name': 'NVIDIA',          'market': 'NASDAQ'},
            {'code': 'TSLA',   'name': 'Tesla',           'market': 'NASDAQ'},
            {'code': 'GOOGL',  'name': 'Alphabet',        'market': 'NASDAQ'},
            {'code': 'AMZN',   'name': 'Amazon',          'market': 'NASDAQ'},
            {'code': 'META',   'name': 'Meta Platforms',  'market': 'NASDAQ'},
        ]
        return pd.DataFrame(fallback)

    result = pd.concat(frames, ignore_index=True)
    result['name']       = result['name'].fillna('').str.strip()
    result['code']       = result['code'].fillna('').str.strip()
    # search_key: 이름+코드를 합쳐서 검색에 활용
    result['search_key'] = result['name'] + ' (' + result['code'] + ') [' + result['market'] + ']'
    result = result.dropna(subset=['code']).drop_duplicates(subset='code')
    return result


def search_stocks(query: str, universe: pd.DataFrame, max_results: int = 80):
    """쿼리로 종목 필터링 (이름 또는 코드 포함 검색)."""
    if not query.strip():
        return universe.head(max_results)
    q = query.strip().lower()
    mask = (
        universe['name'].str.lower().str.contains(q, na=False) |
        universe['code'].str.lower().str.contains(q, na=False)
    )
    return universe[mask].head(max_results)
