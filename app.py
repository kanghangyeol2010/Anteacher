import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv

from core.data_fetcher import fetch_stock_data, fetch_fred_data, fetch_news_rss
from core.calculus import calculate_derivatives, get_market_vibe, detect_golden_cross
from core.sentiment import get_market_sentiment_index
from core.ai_orchestrator import generate_report, generate_quick_summary, generate_recommendation_reason
from core.notifier import check_and_alert
from core.stock_list import load_stock_universe
from core.recommender import get_anteacher_recommendations

# Load stock list
stock_universe = load_stock_universe()

# Cache AI report to avoid redundant API calls (TTL: 10 minutes)
@st.cache_data(ttl=600, show_spinner=False)
def cached_report(ticker, latest_close, latest_slope, latest_acc, macro_val, sentiment_score):
    """Thin cached wrapper – pass only hashable primitives."""
    import pandas as pd
    # Reconstruct minimal DataFrames from primitives for the orchestrator
    stock_stub = pd.DataFrame({
        'Close': [latest_close, latest_close],
        'Slope': [latest_slope, latest_slope],
        'Acceleration': [latest_acc, latest_acc],
    })
    macro_stub = pd.DataFrame({'value': [macro_val]}) if macro_val != "N/A" else None
    return generate_report(stock_stub, macro_stub, sentiment_score, ticker)

load_dotenv()

# ─────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="안테처 (Anteacher) – AI 금융 교육 플랫폼",
    layout="wide",
    page_icon="🐜",
)

# 모든 UI 요소를 숨기는 마법의 CSS (사이드바 버튼 복구 버전)
hide_st_style = """
            <style>
            /* 1. 우측 상단 지저분한 요소 제거 */
            [data-testid="stHeaderActionElements"], .stAppDeployButton, #MainMenu {
                display: none !important;
            }
            /* 2. 하단 푸터 제거 */
            footer { visibility: hidden; }
            /* 3. 헤더 투명화 및 화살표 버튼 복구 */
            header { background-color: rgba(0,0,0,0) !important; }
            button[data-testid="stSidebarCollapseIcon"], button[aria-label="Open sidebar"] {
                visibility: visible !important;
                color: #40c4ff !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ─────────────────────────────────────────
# Global CSS – Finance Dark Blue Theme
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+KR:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans KR', sans-serif;
}

/* ── App background ── */
.stApp { background: #060d1b; }
section[data-testid="stSidebar"] { background: #0b1629 !important; border-right: 1px solid #1e3a5f; }

/* ── Sidebar text ── */
section[data-testid="stSidebar"] * { color: #c9d8f0 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #1565c0, #0288d1) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.6rem 0 !important;
    transition: transform 0.2s, box-shadow 0.2s;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(2,136,209,0.5);
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: #0d1f3c;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 18px 22px !important;
}
div[data-testid="metric-container"] label { color: #7da8d8 !important; font-size: 0.85rem !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8f4fd !important; font-size: 1.8rem !important; font-weight: 700 !important; }

/* ── Tab styling ── */
button[data-baseweb="tab"] {
    background: transparent !important;
    color: #7da8d8 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    border-bottom: 3px solid transparent !important;
    padding-bottom: 8px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #40c4ff !important;
    border-bottom: 3px solid #40c4ff !important;
}

/* ── Page title ── */
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #40c4ff 0%, #82b1ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.hero-sub { color: #4a7ab5; font-size: 1.05rem; margin-bottom: 1.5rem; }

/* ── Info boxes ── */
.teacher-box {
    background: rgba(2,136,209,0.08);
    border-left: 5px solid #0288d1;
    padding: 22px;
    border-radius: 8px;
    color: #c9d8f0;
    line-height: 1.8;
}
.wrong-note {
    background: rgba(239,83,80,0.08);
    border-left: 5px solid #ef5350;
    padding: 22px;
    border-radius: 8px;
    color: #f4c2c2;
    line-height: 1.8;
    margin-top: 16px;
}
.news-card {
    background: #0d1f3c;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 10px;
    color: #c9d8f0;
}
.news-card a { color: #40c4ff; text-decoration: none; }
.news-card a:hover { text-decoration: underline; }
.news-tag { font-size: 0.75rem; color: #4a7ab5; margin-top: 4px; }

/* ── Welcome screen ── */
.welcome-card {
    background: #0d1f3c;
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 36px;
    text-align: center;
    color: #c9d8f0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Helper: emoji for market condition
# ─────────────────────────────────────────
def market_emoji(slope, acc):
    if slope > 0 and acc > 0:
        return "🚀"
    elif slope > 0 and acc < 0:
        return "📈"
    elif slope < 0 and acc > 0:
        return "🔄"
    else:
        return "📉"

# ─────────────────────────────────────────
# SIDEBAR – All Inputs
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐜 안테처")
    st.caption("수학으로 보는 금융 교육 플랫폼")
    st.divider()

    st.markdown("### 🔍 종목 설정")
    selected_stock_key = st.selectbox(
        "종목 검색 (이름 또는 티커)",
        options=stock_universe['search_key'].tolist(),
        index=int(stock_universe[stock_universe['code'] == 'NVDA'].index[0]) if 'NVDA' in stock_universe['code'].values else 0,
        help="삼성전자, AAPL 등 이름이나 티커를 입력해보세요."
    )
    
    # Extract ticker from search_key
    selected_stock_info = stock_universe[stock_universe['search_key'] == selected_stock_key].iloc[0]
    ticker = selected_stock_info['code']
    stock_name = selected_stock_info['name']

    period = st.selectbox("분석 기간", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    ma_window = st.slider(
        "이동평균 창(SMA)", 3, 20, 5, 
        help="SMA(Simple Moving Average): 주가의 소음을 줄여 추세를 더 잘 보이게 하는 평균값이에요."
    )

    st.divider()
    st.divider()
    st.markdown("### ⚙️ 분석 옵션")
    use_fred = st.checkbox("거시경제(FRED) 연동", value=True)
    use_news = st.checkbox("뉴스 감성 분석", value=True)
    use_ai = st.checkbox("AI 리포트 생성", value=True)
    show_gc = st.checkbox("🟡 골든크로스 표시", value=True, help="주가가 다시 힘차게 올라가기 시작하는 '골든크로스' 지점을 차트에 표시합니다.")

    st.divider()
    analyze_btn = st.button("📊 분석 시작하기", use_container_width=True)

    st.divider()
    st.markdown("### 🛠 시스템")
    st.caption("Calculus Engine v1.0")
    st.caption("AI Brain: Gemini 1.5 Flash")
    st.caption("Data: yfinance / FDR / FRED")

# ─────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────
st.markdown("<h1 class='hero-title'>안테처 (Anteacher)</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-sub'>미분으로 읽는 시장 · 감성으로 듣는 뉴스 · AI로 쓰는 투자 리포트</p>", unsafe_allow_html=True)

if not analyze_btn:
    st.markdown("<h2 style='color:#40c4ff; margin-bottom:20px'>🍎 오늘의 안테처 추천 종목</h2>", unsafe_allow_html=True)
    
    with st.spinner("🔍 시장 대장주 중 상승 에너지가 강한 종목을 찾는 중..."):
        recommends = get_anteacher_recommendations(limit=3)
    
    if recommends:
        cols = st.columns(3)
        for i, rec in enumerate(recommends):
            currency_symbol = "₩" if rec['market'] == "KRX" else "$"
            formatted_price = f"{rec['close']:,.0f}" if rec['market'] == "KRX" else f"{rec['close']:,.2f}"
            
            # cache mismatch 방지를 위해 .get() 사용
            prob_high = rec.get('rise_prob', 0)
            prob_low  = rec.get('rise_prob_low', max(prob_high - 15, 0))
            prob_text = f"{prob_low}% ~ {prob_high}%"
            
            likelihood_label = ""
            if prob_high >= 90:
                likelihood_label = "<div style='color:#ffeb3b; font-size:0.8rem; margin-top:4px'>🔥 상승 가능성 매우 높음 (강력 추천)</div>"
            
            with cols[i]:
                st.markdown(f"""
                <div style='background:#0d1f3c; border:1px solid #1e3a5f; border-radius:16px; padding:20px; height:450px'>
                    <h3 style='color:#40c4ff; margin-bottom:5px'>{rec['name']}</h3>
                    <p style='color:#7da8d8; font-size:0.9rem'>{rec['code']}</p>
                    <h2 style='color:#e8f4fd'>{currency_symbol}{formatted_price}</h2>
                    <div style='background:rgba(64,196,255,0.1); padding:10px; border-radius:8px; margin:15px 0'>
                        <div style='color:#40c4ff; font-weight:700; font-size:1.1rem'>상승 확률: {prob_text}</div>
                        {likelihood_label}
                    </div>
                    <div style='color:#4a7ab5; font-size:0.7rem; line-height:1.4; margin-top:10px'>
                        ※ 본 수치는 과거 데이터와 AI 분석 결과일 뿐, 실제 투자 수익을 보장하지 않습니다.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Small sparkline
                spark_fig = go.Figure()
                spark_fig.add_trace(go.Scatter(x=rec['df'].index, y=rec['df']['Close'], line=dict(color='#40c4ff', width=2)))
                spark_fig.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                spark_fig.update_xaxes(visible=False); spark_fig.update_yaxes(visible=False)
                st.plotly_chart(spark_fig, use_container_width=True, config={'displayModeBar': False})
                
                # AI Reason
                reason = generate_recommendation_reason(rec['code'], rec['name'], rec['slope'], rec['sentiment'])
                st.info(reason)
    else:
        st.warning("⚠️ 현재 추천 종목을 불러올 수 없습니다. 잠시 후 다시 시도하거나 사이드바에서 직접 검색해주세요.")


    st.markdown("""
    <div class='welcome-card' style='margin-top:30px'>
        <h3 style='color:#7da8d8'>👈 더 자세한 분석을 원하시면 왼쪽에서 검색하세요!</h3>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────
# Data Fetching & Processing
# ─────────────────────────────────────────
with st.spinner("🤖 AI가 열심히 분석 중입니다... 잠시만 기다려주세요!"):
    stock_df = fetch_stock_data(ticker, period=period)
    fred_df = fetch_fred_data() if use_fred else None
    news_rss = fetch_news_rss(ticker) if use_news else []
    sentiment_score = get_market_sentiment_index(news_rss) if use_news else 0.0

if stock_df is None or stock_df.empty:
    st.error("❌ 데이터를 가져오지 못했습니다. 티커 코드를 확인하세요.")
    st.stop()

stock_df = calculate_derivatives(stock_df, window=ma_window)
check_and_alert(stock_df, ticker, stock_name)

latest_close = stock_df['Close'].iloc[-1]
prev_close   = stock_df['Close'].iloc[-2]
latest_slope = stock_df['Slope'].iloc[-1]
prev_slope   = stock_df['Slope'].iloc[-2]
latest_acc   = stock_df['Acceleration'].iloc[-1]
vibe         = get_market_vibe(latest_slope, latest_acc)
emoji        = market_emoji(latest_slope, latest_acc)

# ─────────────────────────────────────────
# TOP METRICS DASHBOARD
# ─────────────────────────────────────────
st.markdown(f"### {emoji} **{stock_name} ({ticker.upper()})** 실시간 지표")

# ── Anteacher Quick Summary Section ──
with st.container():
    st.markdown("""
    <div style='background:rgba(64,196,255,0.05); border:1px solid #40c4ff; border-radius:12px; padding:20px; margin-bottom:25px;'>
        <h4 style='margin-top:0; color:#40c4ff;'>🍎 안테처의 퀵 요약 리포트</h4>
    """, unsafe_allow_html=True)
    
    with st.spinner("⚡ 요약 리포트 생성 중..."):
        quick_summary = generate_quick_summary(ticker, stock_name, latest_slope, latest_acc, sentiment_score)
        st.markdown(f"<div style='color:#e8f4fd; line-height:1.6;'>{quick_summary}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    main_curr = "₩" if ticker.isdigit() else "$"
    if ticker.isdigit():
        formatted_latest = f"{latest_close:,.0f}"
        formatted_delta  = f"{latest_close - prev_close:+,.0f}"
    else:
        formatted_latest = f"{latest_close:,.2f}"
        formatted_delta  = f"{latest_close - prev_close:+,.2f}"
    
    st.metric("현재 주가", f"{main_curr}{formatted_latest}", formatted_delta)
with c2:
    st.metric("기울기 (Slope)", f"{latest_slope:.4f}", f"{latest_slope - prev_slope:+.4f}", 
              help="주가가 지금 얼마나 빨리 오르거나 내리고 있는지를 나타내는 수치예요. 자전거 페달을 얼마나 세게 밟고 있는지와 비슷하답니다!")
with c3:
    st.metric("가속도 (Acceleration)", f"{latest_acc:.4f}", 
              help="주가의 상승/하락 속도가 더 빨라지고 있는지, 아니면 힘이 빠지고 있는지를 알려주는 지표예요. 엔진의 추진력이라고 생각하면 쉬워요!")
with c4:
    label = "😊 긍정적" if sentiment_score > 0.1 else ("😨 부정적" if sentiment_score < -0.1 else "😐 중립")
    st.metric("뉴스 심리 지수", f"{sentiment_score:.2f}", label,
              help="인터넷의 최신 뉴스들을 AI가 읽고 분위기가 좋은지 나쁜지를 점수화한 거예요. 1에 가까울수록 아주 좋은 소식이 많다는 뜻이에요!")

st.divider()

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📐 수학적 분석", "📰 뉴스 리서치", "📝 안테처의 오답 노트"])

# ══════════════════════════════════════════
# TAB 1 – 수학적 분석
# ══════════════════════════════════════════
with tab1:
    st.subheader("📊 Calculus Engine 시각화")
    st.caption("마우스를 올리면 정확한 수치를 확인할 수 있습니다. 🟡 골든크로스 지점은 차트에 화살표로 표시됩니다.")

    # ── 골든크로스 탐지: 5일선이 20일선을 돌파하는 지점
    gc_dates = detect_golden_cross(stock_df) if show_gc else []
    golden_crosses = []
    for d in gc_dates:
        golden_crosses.append((d, stock_df.loc[d, 'Close']))

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=("💵 Price (주가)", "📈 1st Derivative – Slope (기울기)", "⚡ 2nd Derivative – Acceleration (가속도)")
    )

    # Price + candlestick area
    fig.add_trace(go.Scatter(
        x=stock_df.index, y=stock_df['Close'],
        name="Price", line=dict(color='#40c4ff', width=2),
        fill='tozeroy', fillcolor='rgba(64,196,255,0.07)',
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>종가: $%{y:,.2f}<extra></extra>"
    ), row=1, col=1)

    # MA5 & MA20
    fig.add_trace(go.Scatter(
        x=stock_df.index, y=stock_df['MA5'],
        name="MA5 (5일선)", line=dict(color='#ffeb3b', width=1, dash='dot'),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=stock_df.index, y=stock_df['MA20'],
        name="MA20 (20일선)", line=dict(color='#ff7043', width=1, dash='dot'),
    ), row=1, col=1)

    # Slope bars
    colors_slope = ['#26c6da' if v >= 0 else '#ef5350' for v in stock_df['Slope']]
    fig.add_trace(go.Bar(
        x=stock_df.index, y=stock_df['Slope'],
        name="Slope", marker_color=colors_slope,
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>기울기: %{y:.4f}<extra></extra>"
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=stock_df.index, y=stock_df['Slope_SMA'],
        name="Slope SMA", line=dict(color='#fff59d', width=1.5, dash='dot'),
        hovertemplate="SMA: %{y:.4f}<extra></extra>"
    ), row=2, col=1)

    # Acceleration bars
    colors_acc = ['#ab47bc' if v >= 0 else '#ff7043' for v in stock_df['Acceleration']]
    fig.add_trace(go.Bar(
        x=stock_df.index, y=stock_df['Acceleration'],
        name="Acceleration", marker_color=colors_acc,
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>가속도: %{y:.4f}<extra></extra>"
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=stock_df.index, y=stock_df['Acceleration_SMA'],
        name="Acc SMA", line=dict(color='#fff59d', width=1.5, dash='dot'),
        hovertemplate="SMA: %{y:.4f}<extra></extra>"
    ), row=3, col=1)

    # ── 골든크로스 어노테이션 추가
    annotations = []
    if show_gc:
        for gc_date, gc_price in golden_crosses:
            annotations.append(dict(
                x=gc_date,
                y=gc_price,
                xref='x', yref='y',
                text='⭐ 골든크로스!',
                showarrow=True,
                arrowhead=2,
                arrowcolor='#ffeb3b',
                arrowsize=1.5,
                arrowwidth=2,
                ax=0, ay=-40,
                font=dict(color='#ffeb3b', size=11),
                bgcolor='rgba(0,0,0,0.6)',
                bordercolor='#ffeb3b',
                borderwidth=1,
            ))

    fig.update_layout(
        height=750,
        template="plotly_dark",
        paper_bgcolor='#060d1b',
        plot_bgcolor='#0b1629',
        showlegend=False,
        hovermode='x unified',
        margin=dict(l=0, r=0, t=40, b=0),
        annotations=annotations
    )
    fig.update_xaxes(showgrid=True, gridcolor='#1e3a5f', zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#1e3a5f', zeroline=True, zerolinecolor='#2a4a7f')

    if golden_crosses:
        st.success(f"🟡 **골든크로스 {len(golden_crosses)}회 감지!** 기울기가 마이너스에서 플러스로 전환된 지점입니다. 주가가 다시 힘을 얻기 시작한 순간이에요!")
    else:
        st.info("분석 기간 내 골든크로스 미감지 — 기간을 늘려보세요.")

    st.plotly_chart(fig, use_container_width=True)

    # Market Vibe
    st.info(f"**📡 현재 시장 바이브:** {vibe}")

    # Macro Correlation
    if fred_df is not None:
        st.subheader("🏦 거시경제 상관관계 (미국 10년물 국채 vs 주가 기울기)")
        # Align dates – FRED index is DatetimeIndex but may have tz issues
        try:
            fred_df.index = pd.to_datetime(fred_df.index).tz_localize(None)
            stock_idx = pd.to_datetime(stock_df.index).tz_localize(None) if stock_df.index.tz else stock_df.index
            common = stock_idx.intersection(fred_df.index)
            if not common.empty:
                corr_fig = go.Figure()
                corr_fig.add_trace(go.Scatter(
                    x=common, y=stock_df.set_index(stock_idx).loc[common, 'Slope_SMA'],
                    name="주가 기울기 SMA", line=dict(color='#40c4ff'),
                    hovertemplate="기울기: %{y:.4f}<extra></extra>"
                ))
                corr_fig.add_trace(go.Scatter(
                    x=common, y=fred_df.loc[common, 'value'],
                    name="미국 10Y 금리", line=dict(color='#ff7043'),
                    yaxis="y2",
                    hovertemplate="금리: %{y:.2f}%<extra></extra>"
                ))
                corr_fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor='#060d1b',
                    plot_bgcolor='#0b1629',
                    yaxis=dict(title="주가 기울기"),
                    yaxis2=dict(title="10Y 금리 (%)", overlaying="y", side="right"),
                    hovermode='x unified',
                    height=380,
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(corr_fig, use_container_width=True)
        except Exception as e:
            st.warning(f"거시경제 차트 로딩 오류: {e}")

# ══════════════════════════════════════════
# TAB 2 – 뉴스 리서치
# ══════════════════════════════════════════
with tab2:
    st.subheader("📰 관련 최신 뉴스")

    if not news_rss:
        st.info("뉴스를 가져오지 못했거나 분석 옵션이 꺼져 있습니다.")
    else:
        # Sentiment gauge
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment_score,
            delta={'reference': 0, 'valueformat': '.2f'},
            gauge={
                'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': '#40c4ff'},
                'bar': {'color': '#40c4ff'},
                'bgcolor': '#0b1629',
                'bordercolor': '#1e3a5f',
                'steps': [
                    {'range': [-1, -0.3], 'color': '#b71c1c'},
                    {'range': [-0.3, 0.3], 'color': '#1e3a5f'},
                    {'range': [0.3, 1], 'color': '#1b5e20'},
                ],
                'threshold': {'line': {'color': '#fff', 'width': 3}, 'thickness': 0.75, 'value': sentiment_score}
            },
            title={'text': "시장 심리 지수", 'font': {'color': '#c9d8f0', 'size': 16}},
            number={'font': {'color': '#40c4ff', 'size': 36}}
        ))
        gauge_fig.update_layout(
            paper_bgcolor='#060d1b',
            height=280,
            margin=dict(l=30, r=30, t=20, b=10)
        )
        st.plotly_chart(gauge_fig, use_container_width=True)

        st.markdown("---")
        for item in news_rss:
            title = item.get('title', '제목 없음')
            link  = item.get('link', '#')
            pub   = item.get('published', '')
            st.markdown(f"""
            <div class='news-card'>
                <a href='{link}' target='_blank'>{title}</a>
                <div class='news-tag'>🕐 {pub}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3 – 안테처의 오답 노트 (AI Report)
# ══════════════════════════════════════════
with tab3:
    st.subheader(f"🍎 안테처의 AI 심층 리포트  {emoji}")

    if not use_ai:
        st.info("AI 리포트 옵션이 꺼져 있습니다. 사이드바에서 켜주세요.")
    else:
        with st.spinner("✍️ 안테처 선생님이 리포트를 작성하고 있습니다..."):
            macro_val_str = str(fred_df['value'].dropna().iloc[-1]) if fred_df is not None and not fred_df.empty else "N/A"
            report = cached_report(
                ticker,
                float(latest_close),
                float(latest_slope),
                float(latest_acc),
                macro_val_str,
                float(sentiment_score),
            )

        if "투명한 오답 노트" in report:
            parts = report.split("투명한 오답 노트", 1)
            main_report = parts[0]
            wrong_note  = parts[1]
        else:
            main_report = report
            wrong_note  = ""

        # ── 3줄 요약 추출 & 강조 카드
        SUMMARY_KEY = "초보자를 위한 3줄 요약"
        if SUMMARY_KEY in main_report:
            body, summary = main_report.split(SUMMARY_KEY, 1)
            st.markdown(f"<div class='teacher-box'>{body}</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0d2b4e,#1a3d6e);
                        border:2px solid #40c4ff; border-radius:14px;
                        padding:24px; margin-top:20px;'>
                <h3 style='color:#40c4ff; margin-bottom:14px'>⭐ 초보자를 위한 3줄 요약</h3>
                <div style='color:#e8f4fd; font-size:1.05rem; line-height:2'>{summary}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='teacher-box'>{main_report}</div>", unsafe_allow_html=True)

        if wrong_note:
            st.markdown(f"<div class='wrong-note'><h4>📝 안테처의 투명한 오답 노트</h4>{wrong_note}</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='wrong-note'>
                <h4>📝 안테처의 투명한 오답 노트</h4>
                <p>• 미분 기반 분석은 <b>후행 지표</b>입니다. 갑작스러운 외부 이슈(공시, 지정학적 리스크 등)에는 대응이 늦을 수 있어요.</p>
                <p>• 뉴스 감성 점수는 영문 기사 중심으로 산출되어 한국 기업의 국내 이슈가 누락될 수 있습니다.</p>
                <p>• 과거 데이터 기반 분석이므로 미래를 <b>예측</b>하는 것이 아닌, 현재 <b>흐름을 이해</b>하는 데 활용하세요.</p>
            </div>
            """, unsafe_allow_html=True)

        st.caption("⚠️ 이 리포트는 교육 목적으로 제공되며 투자 권유가 아닙니다.")

