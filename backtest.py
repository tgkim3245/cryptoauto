import pyupbit
import numpy as np

""" 
백테스트 전용
"""
# def backtest(dict_tickers):
#     for ticker, df in dict_tickers.items():
#         if df['state']

# OHLCV(open, high, low, close, volume, value)로 당일 시가, 고가, 저가, 종가, 거래량, 거래금액에 대한 데이터
df = pyupbit.get_ohlcv("KRW-BTC", count=220)

# 변동폭 * k 계산, (고가 - 저가) * k값
df['range'] = (df['high'] - df['low']) * 0.2

# target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
df['target'] = df['open'] + df['range'].shift(1)

# ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],
                     1)

# 누적 곱 계산(cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()

# Draw Down(하락률) 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

#MDD(최대 하락률) 계산
print("최대하락률(%): ", df['dd'].max())
print("최대수익률(%): ", df['ror'].max())
print("최대손실률(%): ", df['ror'].min())


#엑셀로 출력
df.to_excel("backtest.xlsx")