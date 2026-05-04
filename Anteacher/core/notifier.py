import requests
# forced reload comment
import os
from dotenv import load_dotenv

load_dotenv()

def send_discord_alert(message):
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        return
    
    data = {
        "content": f"🚀 **[Anteacher Alert]**\n{message}"
    }
    
    try:
        response = requests.post(webhook_url, json=data)
        return response.status_code == 204
    except Exception as e:
        print(f"Discord alert error: {e}")
        return False

def check_and_alert(df, ticker, stock_name="Unknown"):
    """
    주가 기울기의 급격한 변화를 감지하여 디스코드 알림을 전송합니다.
    """
    if df is None or len(df) < 2:
        return
    
    latest_close = df['Close'].iloc[-1]
    latest_slope = df['Slope'].iloc[-1]
    prev_slope = df['Slope'].iloc[-2]
    
    # ── 가독성 개선 계산
    # 1. 기울기를 현재가 대비 비율(%)로 변환
    slope_percent = (latest_slope / latest_close) * 100
    # 2. 가속도(변화량)를 현재가 대비 비율(%)로 변환
    change_raw = latest_slope - prev_slope
    change_percent = (change_raw / latest_close) * 100
    
    # ── 문장형 설명 생성
    direction = "상승세" if change_raw > 0 else "하락세"
    steepness = "가팔라졌습니다" if (latest_slope * change_raw) > 0 else "완만해졌습니다"
    acc_desc = f"이전보다 {direction}가 {abs(change_percent):.1f}% 더 {steepness}"
    
    print(f"[DEBUG] Notifier Triggered for {ticker}. Change Percent: {change_percent:.4f}%")
    
    # 임계값 없이 모든 분석 결과를 디스코드로 전송합니다.
    msg = (
        f"📍 **{stock_name}({ticker})** 분석 리포트 도착!\n"
        f"📉 **현재 기울기**: {slope_percent:+.1f}% (현재가 대비)\n"
        f"⚡ **가속도 분석**: {acc_desc}\n"
        f"🐜 안테처 선생님의 상세 분석이 완료되었습니다!"
    )
    success = send_discord_alert(msg)
    print(f"[DEBUG] Alert sent status: {success}")
