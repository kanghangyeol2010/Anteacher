import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# gemini-2.0-flash-lite: 가장 저렴한 Gemini 모델 (우선 사용)
MODEL_FALLBACKS = [
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
]

def _call_with_fallback(prompt):
    """Try each model in order, fall back on quota/not-found errors."""
    last_err = None
    for model_name in MODEL_FALLBACKS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            err_str = str(e)
            # Retry after suggested delay on 429
            if '429' in err_str and 'retry_delay' in err_str:
                # Try to parse retry seconds
                try:
                    delay = int(err_str.split('seconds:')[1].split('}')[0].strip())
                except Exception:
                    delay = 30
                print(f"[Anteacher] {model_name} 할당량 초과 - {delay}초 대기 후 다음 모델로 전환...")
                time.sleep(min(delay, 30))  # cap at 30s to keep UI responsive
            elif '404' in err_str:
                print(f"[Anteacher] {model_name} 모델 없음 - 다음 모델 시도...")
            else:
                print(f"[Anteacher] {model_name} 오류: {e}")
            last_err = e
    return f"⚠️ 모든 모델에서 보고서 생성에 실패했습니다.\n\n마지막 오류: {last_err}"


def generate_quick_summary(ticker: str, stock_name: str, slope: float, acc: float, sentiment: float) -> str:
    """
    빠른 3줄 요약 — 사이드바 종목 선택 직후 즉시 표시.
    최대한 짧게 (200자 내외).
    """
    prompt = f"""
당신은 친절한 금융 선생님 안테처입니다.
다음 데이터를 보고 초등학생도 이해할 수 있게 딱 3줄로 요약해주세요.
절대 3줄을 넘기지 마세요.

- 종목: {stock_name} ({ticker})
- 기울기(주가 속도): {slope:.4f}  (양수=오르는 중, 음수=내리는 중)
- 가속도(속도 변화): {acc:.4f}   (양수=가속, 음수=둔화)
- 뉴스 감성: {sentiment:.2f}   (1에 가까울수록 긍정)

출력 형식 (이 형식 그대로):
📈 상승 확률: [XX% ~ XX% 사이] — 절대 95%를 넘기지 마세요.
💰 예상 변동: [±X%~±X%] (1주일 기준)
🔑 한마디: [초등학생도 이해하는 핵심 이유 한 문장]
※ 본 분석은 참고용이며 투자 수익을 보장하지 않습니다.
"""
    return _call_with_fallback(prompt)


def generate_report(stock_data, macro_data, news_sentiment, ticker):
    """
    Generates a financial report using Gemini with automatic model fallback.
    Includes CoT reasoning and follows a teacher persona.
    """
    latest_price = stock_data['Close'].iloc[-1]
    latest_slope = stock_data['Slope'].iloc[-1]
    latest_acc   = stock_data['Acceleration'].iloc[-1]
    macro_val    = macro_data['value'].dropna().iloc[-1] if macro_data is not None and not macro_data.empty else "N/A"

    prompt = f"""
당신은 친절한 금융 선생님 '안테처(Anteacher)'입니다.
주식 투자를 처음 시작하는 초보자도 완전히 이해할 수 있도록 쉽고 재미있게 설명해주세요.
어려운 용어를 쓸 땐 반드시 괄호 안에 쉬운 말로 설명해주세요.
예) 기울기(주가가 올라가는 속도), 가속도(그 속도가 더 빨라지는지 느려지는지)

[분석 데이터]
- 종목: {ticker}
- 현재가: {latest_price:.2f}
- 기울기(Slope): {latest_slope:.4f}  ← 양수면 오르는 중, 음수면 내리는 중
- 가속도(Acceleration): {latest_acc:.4f}  ← 양수면 속도가 빨라지는 중
- 미국 10년물 국채 금리: {macro_val}
- 뉴스 감성 점수: {news_sentiment:.2f}  ← 1에 가까울수록 좋은 뉴스

[리포트 구성 – 반드시 이 순서대로 작성하세요]

1. 📊 지금 주가는 어떤 상태인가요?
   - 기울기와 가속도를 자전거 오르막/내리막 비유로 설명해주세요.
   - 뉴스 분위기도 한 줄로 요약해주세요.

2. 🏦 경제 전체 분위기는요?
   - 국채 금리와 주가의 관계를 초등학생도 이해하는 수준으로 설명해주세요.

3. 💬 안테처 선생님의 한마디
   - 친근한 말투로 조언을 해주세요.

4. 투명한 오답 노트
   - 이 분석이 틀릴 수 있는 이유 2가지를 솔직하게 알려주세요.

---
[⭐ 초보자를 위한 3줄 요약] ← 반드시 이 제목을 그대로 써주세요

1) 📈 다음 1주일 상승 확률: (예: 60% ~ 75% 사이) — 절대 95%를 넘기지 말고 범위로 표현하세요.
2) 💰 예상 수익률 범위: (예: -3% ~ +5% 사이) — 보수적으로 추정
3) 🔑 핵심 이유 한 줄: (초등학생도 이해하는 말로) — 기울기와 뉴스 감성을 합쳐서

※ 마지막에 반드시 "**본 분석은 참고용이며 투자 수익을 보장하지 않습니다.**"라는 경고 문구를 포함하세요.

보고서는 한글로 작성하고, 각 항목을 이모지와 함께 명확히 구분해 주세요.
"""
    return _call_with_fallback(prompt)


def generate_recommendation_reason(ticker: str, stock_name: str, slope: float, sentiment: float) -> str:
    """
    오늘의 추천 종목에 대한 아주 짧은 한 줄 요약 사유 생성.
    """
    prompt = f"""
금융 선생님 안테처로서 다음 종목의 추천 사유를 '초보자도 이해할 수 있게' 딱 한 줄(40자 이내)로 요약해주세요.
이모지를 섞어서 친절하게 말해주세요.

- 종목: {stock_name} ({ticker})
- 기울기(상승 속도): {slope:.4f}
- 뉴스 분위기: {sentiment:.2f} (1에 가까울수록 좋음)

출력 형식:
(한 줄 요약 내용)
"""
    return _call_with_fallback(prompt).strip()

def get_comprehensive_analysis(ticker, stock_name, stock_df, macro_val, local_news, global_news):
    """
    Consolidates sentiment, summary, and full report into a single Gemini call.
    Returns a dictionary with all components.
    """
    latest_price = stock_df['Close'].iloc[-1]
    latest_slope = stock_df['Slope'].iloc[-1]
    latest_acc   = stock_df['Acceleration'].iloc[-1]
    
    local_h = "\n".join([f"- {n.get('title','')}" for n in local_news[:5]])
    global_h = "\n".join([f"- {n.get('title','')}" for n in global_news[:5]])
    
    prompt = f"""
당신은 최고의 금융 AI 선생님 '안테처'입니다. 다음 데이터를 종합 분석하여 반드시 지정된 JSON 형식으로만 답변하세요.

[분석 데이터]
- 종목: {stock_name} ({ticker})
- 현재가: {latest_price:.2f} / 기울기: {latest_slope:.4f} / 가속도: {latest_acc:.4f}
- 거시경제(금리): {macro_val}
- 국내 뉴스: {local_h}
- 해외 뉴스: {global_h}

[JSON 구조 요구사항]
{{
  "sentiment": -1.0에서 1.0 사이의 숫자 (뉴스 분위기),
  "quick_summary": "📈 상승 확률: XX%~XX% 등 딱 3줄 요약",
  "report_main": "본문 리포트 내용 (이모지 포함)",
  "wrong_note": "📝 투명한 오답 노트 내용 (분석의 한계점)",
  "rec_reason": "오늘의 추천 한줄평 (40자 이내)"
}}

반드시 유효한 JSON 형식으로, 다른 텍스트 없이 JSON만 출력하세요.
"""
    response_text = _call_with_fallback(prompt)
    
    try:
        # Extract JSON block
        json_match = re.search(r"({.*})", response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
            return data
    except Exception as e:
        print(f"[Anteacher] JSON Parsing Error: {e}")
    
    # Fallback in case of failure (handles 429 Quota errors cleanly)
    return {
        "sentiment": 0.0,
        "quick_summary": "⚠️ 안테처의 두뇌(AI)가 너무 많은 요청으로 잠시 쉬고 있습니다. (API 한도 초과)",
        "report_main": f"<h3>🚨 AI 리포트 생성 지연</h3><p>현재 사용자 요청이 너무 많아 무료 AI API 일시적 한도를 초과했습니다. 1~2분 뒤에 다시 시도해주세요.</p><details><summary>디버그 정보 보기</summary><pre style='font-size:0.8rem'>{response_text}</pre></details>",
        "wrong_note": "API 한도 초과로 오답 노트를 생성할 수 없습니다.",
        "rec_reason": "분석 일시 지연 ⏳"
    }

import json
import re

def get_batch_sentiment_and_reason(candidates_data):
    """
    Batch call for recommendation list to save API quota.
    candidates_data: list of dicts with 'code', 'name', 'slope', 'acc', 'news'
    Returns: dict mapping ticker code to {"sentiment": float, "reason": str}
    """
    if not candidates_data:
        return {}
        
    prompt_parts = []
    for item in candidates_data:
        news_list = item.get('news', [])
        headlines = "\n".join([f"- {n.get('title', '')}" for n in news_list[:3]]) if news_list else "뉴스 없음"
        
        part = f"""
[종목: {item['name']} ({item['code']})]
기울기: {item['slope']:.4f} / 가속도: {item['acc']:.4f}
뉴스:
{headlines}
"""
        prompt_parts.append(part)
        
    combined_data = "\n".join(prompt_parts)
    
    prompt = f"""
다음 주식들의 정보를 보고 각 종목별로 1) 뉴스 감성 점수(-1.0 ~ 1.0)와 2) 초보자용 한줄평(40자 이내)을 JSON으로 리턴하세요.
반드시 아래의 [출력 형식]과 동일한 JSON 구조를 반환해야 합니다. 다른 텍스트는 포함하지 마세요.

[데이터]
{combined_data}

[출력 형식]
{{
  "TICKER1": {{"sentiment": 0.25, "reason": "이모지를 포함한 친절한 한줄평"}},
  "TICKER2": {{"sentiment": 0.50, "reason": "또 다른 한줄평"}}
}}
"""
    try:
        res = _call_with_fallback(prompt)
        m = re.search(r"(\{.*\})", res, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            return data
    except Exception as e:
        print(f"[Batch AI Error] {e}")
        pass
        
    # Fallback
    return {item['code']: {"sentiment": 0.0, "reason": "분석 중 오류가 발생했습니다. 🧐"} for item in candidates_data}

def get_gemini_sentiment(news_list):
    # (Keep for backward compatibility or direct calls)
    if not news_list: return 0.0
    headlines = "\n".join([f"- {n.get('title', '')}" for n in news_list])
    prompt = f"다음 뉴스 헤드라인의 분위기를 -1.0 ~ 1.0 사이의 숫자로만 답변하세요:\n{headlines}"
    try:
        res = _call_with_fallback(prompt)
        m = re.search(r"(-?\d+\.?\d*)", res)
        return float(m.group(1)) if m else 0.0
    except: return 0.0
