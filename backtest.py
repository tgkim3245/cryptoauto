import pyupbit
import numpy as np
import pandas as pd
import datetime
import database as db
import indicators as ind

def get_backtest_result(strategy="변동성 돌파", period=30, k=0.5, ticker="KRW-BTC"):
    """백테스팅 결과 반환 (통합 진입점)"""
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=period)
    
    # DB에서 먼저 조회
    df = db.load_ohlcv(ticker, "day", start=start_date.strftime("%Y-%m-%dT%H:%M:%S"))
    
    # 데이터 부족 시 API 호출 및 DB 저장
    # 데이터 부족 시 API 호출 및 DB 저장
    if df is None or len(df) < period:
        df_api = pyupbit.get_ohlcv(ticker, interval="day", count=period+100) # 여유분 확보
        if df_api is not None:
             # DB 저장 전 정렬
            df_api = df_api.sort_index()
            db.save_ohlcv(df_api, ticker, "day")
            
            # DB 데이터와 API 데이터 병합 (결측 구간 보완)
            if df is not None:
                df = pd.concat([df, df_api])
                df = df[~df.index.duplicated(keep='last')] # 중복 제거
            else:
                df = df_api

    if df is None or df.empty:
        return {"error": "데이터를 가져올 수 없습니다."}
        
    # 데이터 정제: 정렬 및 중복 제거, 결측치 처리
    df = df.sort_index()
    df = df[~df.index.duplicated(keep='last')]
    
    # 시작일 이후 데이터만 필터링
    df = df[df.index >= start_date]

    # 전략별 로직 실행
    if strategy == "변동성 돌파":
        return _backtest_volatility_breakout(df, k)
    elif strategy == "RSI 전략":
        return _backtest_rsi_strategy(df)
    elif strategy == "이동평균 크로스":
        return _backtest_ma_cross(df)
    else:
        return _backtest_volatility_breakout(df, k)

def _backtest_volatility_breakout(df, k):
    """변동성 돌파 전략 백테스팅"""
    df = df.copy()
    
    # 1. 변동성 돌파 기준 계산
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    
    # 2. 매수 신호 (고가가 목표가보다 높으면 매수)
    # 수수료 고려 (0.05%)
    fee = 0.0005
    
    df['ror'] = np.where(df['high'] > df['target'],
                         (df['close'] / df['target']) - fee,
                         1)
    
    return _calculate_metrics(df)

def _backtest_rsi_strategy(df):
    """RSI 전략 백테스팅 (RSI < 30 매수, RSI > 70 매도)"""
    df = df.copy()
    
    # 지표 계산 (indicators 모듈 사용)
    df['rsi'] = ind.calculate_rsi(df, 14)
    
    # 매매 로직: RSI < 30 다음날 시가 매수, RSI > 70 다음날 시가 매도 (단순화)
    df['position'] = 0
    current_position = 0 # 0: 미보유, 1: 보유
    positions = []
    
    for i in range(len(df)):
        rsi = df['rsi'].iloc[i]
        if pd.isna(rsi):
            positions.append(current_position)
            continue
            
        if rsi < 30:
            current_position = 1
        elif rsi > 70:
            current_position = 0
        positions.append(current_position)
        
    df['position'] = positions
    
    # 수익률 계산: 전일 포지션이 1이면 당일 등락폭 반영
    df['yield'] = df['close'].pct_change() + 1
    df['ror'] = np.where(df['position'].shift(1) == 1, df['yield'] - 0.0005/100, 1)

    return _calculate_metrics(df)

def _backtest_ma_cross(df):
    """이동평균 크로스 전략 (골든크로스 매수, 데드크로스 매도)"""
    df = df.copy()
    
    df['ma5'] = ind.calculate_ma(df, 5)
    df['ma20'] = ind.calculate_ma(df, 20)
    
    # 포지션: 5일선이 20일선 위에 있으면 보유
    df['position'] = np.where(df['ma5'] > df['ma20'], 1, 0)
    
    df['yield'] = df['close'].pct_change() + 1
    df['ror'] = np.where(df['position'].shift(1) == 1, df['yield'] - 0.0005/100, 1)
    
    return _calculate_metrics(df)

def _calculate_metrics(df):
    """공통 성과 지표 계산"""
    # 결측치 제거 (초기 데이터)
    df = df.dropna(subset=['ror'])
    
    df['cum_ror'] = df['ror'].cumprod()
    
    if len(df) == 0:
        return {"error": "계산 가능한 데이터가 없습니다."}

    total_return = (df['cum_ror'].iloc[-1] - 1) * 100
    
    # CAGR
    days = len(df)
    cagr = (df['cum_ror'].iloc[-1] ** (365 / days) - 1) * 100 if days > 0 else 0
    
    # MDD
    df['high_cum_ror'] = df['cum_ror'].cummax()
    df['dd'] = (df['cum_ror'] / df['high_cum_ror'] - 1) * 100
    mdd = df['dd'].min()
    
    # 승률
    win_days = len(df[df['ror'] > 1])
    total_trade_days = len(df[df['ror'] != 1])
    win_rate = (win_days / total_trade_days * 100) if total_trade_days > 0 else 0
    
    # history 데이터에서 NaN 처리 (JSON 호환성)
    history_data = []
    for index, row in df.iterrows():
        item = {
            "time": int(index.timestamp()),
            "value": float(row['cum_ror'] * 100) if pd.notnull(row['cum_ror']) else 0.0
        }
        history_data.append(item)

    return {
        "total_return": round(total_return, 2) if pd.notnull(total_return) else 0.0,
        "cagr": round(cagr, 2) if pd.notnull(cagr) else 0.0,
        "mdd": round(mdd, 2) if pd.notnull(mdd) else 0.0,
        "win_rate": round(win_rate, 2) if pd.notnull(win_rate) else 0.0,
        # 차트용 데이터 (JSON 직렬화 가능하게 변환)
        "history": history_data
    }

if __name__ == "__main__":
    print(get_backtest_result())
