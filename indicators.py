import pandas as pd
import numpy as np

def calculate_ma(df: pd.DataFrame, window: int, column: str = 'close') -> pd.Series:
    """이동평균선 계산"""
    return df[column].rolling(window=window).mean()

def calculate_bb(df: pd.DataFrame, window: int = 20, k: float = 2.0, column: str = 'close'):
    """볼린저 밴드 계산"""
    ma = df[column].rolling(window=window).mean()
    std = df[column].rolling(window=window).std()
    upper = ma + k * std
    lower = ma - k * std
    return upper, lower

def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
    """RSI (Relative Strength Index) 계산 - Wilder's Smoothing"""
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    # Wilder's Smoothing (alpha = 1/period)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, column: str = 'close'):
    """MACD (Moving Average Convergence Divergence) 계산"""
    exp12 = df[column].ewm(span=fast, adjust=False).mean()
    exp26 = df[column].ewm(span=slow, adjust=False).mean()
    macd = exp12 - exp26
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

def add_all_indicators(df: pd.DataFrame):
    """모든 보조지표를 DataFrame에 추가 (In-place modification)"""
    if df is None or df.empty:
        return

    # 이동평균
    df['ma5'] = calculate_ma(df, 5)   # 기존 ma1
    df['ma20'] = calculate_ma(df, 20) # 기존 ma2
    df['ma60'] = calculate_ma(df, 60)
    
    # 볼린저 밴드 (20일 기준)
    df['bb_upper'], df['bb_lower'] = calculate_bb(df, 20, 2)
    
    # RSI
    df['rsi'] = calculate_rsi(df, 14)
    
    # MACD
    df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(df)
    
    # 호환성을 위해 기존 컬럼명 매핑 (필요 시)
    df['ma1'] = df['ma5']
    df['ma2'] = df['ma20']
