import pandas as pd
import numpy as np

def calculate_derivatives(df, column='Close', window=5):
    """
    Calculates 1st derivative (Slope) and 2nd derivative (Acceleration) of stock prices.
    Uses a rolling window to smooth out noise.
    """
    if df is None or df.empty:
        return df

    # 1st Derivative: Slope (Rate of Change)
    df['Slope'] = df[column].diff()
    
    # 2nd Derivative: Acceleration (Change in Slope)
    df['Acceleration'] = df['Slope'].diff()
    
    # Moving Averages for Golden Cross
    df['MA5'] = df[column].rolling(window=5).mean()
    df['MA20'] = df[column].rolling(window=20).mean()
    
    # Smoothing for visualization
    df['Slope_SMA'] = df['Slope'].rolling(window=window).mean()
    df['Acceleration_SMA'] = df['Acceleration'].rolling(window=window).mean()
    
    return df

def detect_golden_cross(df):
    """
    Detects 5-day MA crossing above 20-day MA.
    Returns list of dates where cross occurred.
    """
    if 'MA5' not in df or 'MA20' not in df:
        return []
    
    crosses = []
    # Shift to compare prev values
    prev_ma5 = df['MA5'].shift(1)
    prev_ma20 = df['MA20'].shift(1)
    
    # Golden Cross: prev_ma5 < prev_ma20 AND curr_ma5 >= curr_ma20
    is_cross = (prev_ma5 < prev_ma20) & (df['MA5'] >= df['MA20'])
    
    cross_dates = df[is_cross].index.tolist()
    return cross_dates

def get_market_vibe(slope, acceleration):
    """
    Interprets the derivatives like a math teacher.
    """
    if slope > 0 and acceleration > 0:
        return "강력한 상승 에너지! (기울기 +, 가속도 +)"
    elif slope > 0 and acceleration < 0:
        return "상승세 둔화, 주의가 필요해요. (기울기 +, 가속도 -)"
    elif slope < 0 and acceleration < 0:
        return "하락 가속화, 조심하세요! (기울기 -, 가속도 -)"
    elif slope < 0 and acceleration > 0:
        return "하락세 진정 중, 반등의 신호일까요? (기울기 -, 가속도 +)"
    else:
        return "횡보 구간입니다."
