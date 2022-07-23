from numpy.core.numeric import NaN
import pyupbit
import pandas as pd
import mplfinance as mpf
import plotly.graph_objects as go
import plotly.subplots as ms
import re
import random

def BollingerBands(df, w=20, k=2):
    # w = 기준 이동평균일 
    # k = 기준 상수
    
    #중심선 (MBB) : n일 이동평균선
    df["BB_mbb"]=df["close"].rolling(w).mean()
    df["BB_ma"+str(w)+"_std"]=df["close"].rolling(w).std()
    
    #상한선 (UBB) : 중심선 + (표준편차 × K)
    #하한선 (LBB) : 중심선 - (표준편차 × K)
    df["BB_ubb"]=df.apply(lambda x: x["BB_mbb"]+k*x["BB_ma"+str(w)+"_std"],1)
    df["BB_lbb"]=df.apply(lambda x: x["BB_mbb"]-k*x["BB_ma"+str(w)+"_std"],1)

    ubb = df['BB_ubb'].iloc[-1]
    mbb = df['BB_mbb'].iloc[-1]
    lbb = df['BB_lbb'].iloc[-1]

    return ubb,mbb,lbb
    

def MovingAverage(df, span):
    df["MA"+str(span)]=df["close"].rolling(span).mean()
    ma = df["MA"+str(span)].iloc[-1]

    return ma


def MovingAvgConvDiv(df,macd_short = 12, macd_long = 26, macd_signal = 9):
    #MACD : 단기(12일) 지수이평선 - 장기(26일) 지수이평선
    #signal : 9일의 MACD 지수이평선
    #oscillator : MACD - signal
    df["MACD_short"]=df["close"].ewm(span=macd_short).mean() 
    df["MACD_long"]=df["close"].ewm(span=macd_long).mean() 
    df["MACD"]=df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
    df["MACD_signal"]=df["MACD"].ewm(span=macd_signal).mean() 
    df["MACD_oscillator"]=df.apply(lambda x:(x["MACD"]-x["MACD_signal"]), axis=1)

    MACD_ = df['MACD'].iloc[-1]
    MACD_signal_ = df['MACD_signal'].iloc[-1]

    return MACD_, MACD_signal_
                            
                                           
def RelativeStrengthIndex(df, RSI_n=14):
    # 상승, 하락분을 알기위해 현재 종가에서 전일 종가를 빼서 데이터프레임에 추가하겠습니다.
    df["RSI_delta"]=df['close'].diff()
    # U(up): n일 동안의 종가 상승 분
    df["RSI_U"]=df["RSI_delta"].apply(lambda x: x if x>0 else 0)
    # D(down): n일 동안의 종가 하락 분 --> 음수를 양수로 바꿔줌
    df["RSI_D"]=df["RSI_delta"].apply(lambda x: x * (-1) if x<0 else 0)
    # AU(average ups): U값의 평균
    df["RSI_AU"]=df["RSI_U"].ewm(com=(RSI_n - 1), min_periods=RSI_n).mean()
    # DU(average downs): D값의 평균
    df["RSI_AD"]=df["RSI_D"].ewm(com=(RSI_n - 1), min_periods=RSI_n).mean()
    df["RSI"] = df.apply(lambda x:x["RSI_AU"]/(x["RSI_AU"]+ x["RSI_AD"]) * 100, axis=1)

    RSI_ = df["RSI"].iloc[-1]

    return RSI_

def drawing_plot(df,*args):
    # https://youngwonhan-family.tistory.com/32
    # https://plotly.com/python/reference/layout/#layout-margin

    fig = ms.make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                            row_heights=[50,10,10,10])

    fig.update_layout(
    title='Samsung stock price',
    yaxis1_title='Stock Price',
    xaxis1_title='periods'  
    )
    
    #거래량
    if 'volume' in args and 'volume' in df.columns:
        print('vol ok')
        volume = go.Bar(x=df.index, y=df['volume'])

        fig.add_trace(volume, row=2, col=1)

        # shared_xaxes 함수는 Figure에 설정된 차트들의 x축을 공유
        fig.update_layout(
            title='Samsung stock price',
            yaxis_title='Stock Price',
            yaxis2_title='Volume',
            xaxis1_title='',
            xaxis2_title='periods',
            xaxis1_rangeslider_visible=False,
            xaxis2_rangeslider_visible=False    
        )

    #캔들
    if 'candle' in args and 'open' in df.columns:
        print('cna ok')
        candle = go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='red', # 상승봉
            decreasing_line_color='blue' # 하락봉
        )
        fig.add_trace(candle,row=1, col=1)
    
    #이동평균선
    color_list = [
        'red', 'green', 'violet','yellow','blue','black',
        'brown','gray','pink', 'yellowgreen',
        'lightblue', 'lightcoral', 'lightgray',
            'lightgreen', 'lightpink',  'lightseagreen',
            'lightskyblue', 'lightslategray', 
             'lightyellow',  'limegreen' ]
    for idx, str in enumerate(iterable=args):
        if re.match("MA*", str) and len(str)>2 and str[2:].isdigit():
            print('ma ok')
            ma = go.Scatter(
                x=df.index, 
                y=df[str], 
                line=dict(color=color_list[idx%len(color_list)], width=2), 
                name=str)
            fig.add_trace(ma, row=1, col=1)

    #볼린저밴드
    if 'BB' in args and 'BB_ubb' in df.columns:
        print('BB ok')
        mbb = go.Scatter(
            x=df.index, 
            y=df['BB_mbb'], 
            line=dict(color='black', width=2), 
            name='BB_mbb')
        ubb = go.Scatter(
            x=df.index, 
            y=df['BB_ubb'], 
            line=dict(color='purple', dash='dash',width=2), 
            name='BB_ubb')
        lbb = go.Scatter(
            x=df.index, 
            y=df['BB_lbb'], 
            line=dict(color='purple', dash='dash', width=2), 
            name='BB_lbb')

        fig.add_trace(mbb, row=1, col=1)
        fig.add_trace(ubb, row=1, col=1)
        fig.add_trace(lbb, row=1, col=1)

    #RSI
    if 'RSI' in args and 'RSI' in df.columns:
        print('RSI ok')
        rsi = go.Scatter(
            x=df.index, 
            y=df['RSI'], 
            line=dict(color='black', width=2), 
            name='RSI')

        fig.update_layout(
            yaxis3_title='RSI',
            xaxis1_title='',
            # xaxis2_title='',
            xaxis3_title='period',
            xaxis1_rangeslider_visible=False,
            # xaxis2_rangeslider_visible=False    
        )

        fig.add_trace(rsi, row=3, col=1)

    #MACD
    if 'MACD' in args and 'MACD' in df.columns:
        
        print('MACD ok')
        macd = go.Scatter(
            x=df.index, 
            y=df['MACD'], 
            line=dict(color='black', width=2), 
            name='MACD')
        signal = go.Scatter(
            x=df.index, 
            y=df['MACD_signal'], 
            line=dict(color='red', width=2), 
            name='MACD_signal')


        fig.add_trace(macd, row=4, col=1) 
        fig.add_trace(signal, row=4, col=1)   

    fig.show()


    fig.write_image('./image/test.jpg')


if __name__ == "__main__":
    df = pyupbit.get_ohlcv('KRW-BTC',interval='day', count=200)
    MovingAverage(df, span=5)
    MovingAverage(df, span=20)
    MovingAverage(df, span=60)
    BollingerBands(df)
    RelativeStrengthIndex(df)
    MovingAvgConvDiv(df)

    print(df)
    drawing_plot(df, 'candle','volume','MA5','MA20','BB','RSI','MACD')

