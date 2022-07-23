from numpy.core.numeric import NaN
import pyupbit
import pandas as pd
import matplotlib.pyplot as plt

BUY = 1
SELL = -1
STAY = 0

class BollingerBands:
    def __init__(self, df) -> None:
        # self.df = df
        w= 20 # 기준 이동평균일 
        k= 2 # 기준 상수
        
        #중심선 (MBB) : n일 이동평균선
        df["mbb"]=df["close"].rolling(w).mean()
        df["ma20_std"]=df["close"].rolling(w).std()
        
        #상한선 (UBB) : 중심선 + (표준편차 × K)
        #하한선 (LBB) : 중심선 - (표준편차 × K)
        df["ubb"]=df.apply(lambda x: x["mbb"]+k*x["ma20_std"],1)
        df["lbb"]=df.apply(lambda x: x["mbb"]-k*x["ma20_std"],1)
        
        # df[["mbb","ma20_std","ubb","lbb"]].fillna(0, inplace=True)
        # df[["mbb","ubb","lbb"]].plot.line(subplots=False)
        # plt.show()
        # print(df)

        self.ubb = df['ubb'].iloc[-1]
        self.lbb = df['lbb'].iloc[-1]
        self.mbb = df['mbb'].iloc[-1]

        df["walking_on_BB"] = df.apply(lambda x: 1 if x['high']>=x['ubb'] else 0, axis=1)

class MovingAverage:
    def __init__(self, df, span) -> None:
        df["MA"+str(span)]=df["close"].rolling(span).mean()
        self.ma = df["MA"+str(span)].iloc[-1]

        # df[["MA10"]].plot.line(subplots=False)

class  MovingAvgConvDiv:
    #MACD : 단기(12일) 지수이평선 - 장기(26일) 지수이평선
    #signal : 9일의 MACD 지수이평선
    #oscillator : MACD - signal
    def __init__(self, df) -> None:
        macd_short, macd_long, macd_signal=12,26,9 #기본값 
        df["MACD_short"]=df["close"].ewm(span=macd_short).mean() 
        df["MACD_long"]=df["close"].ewm(span=macd_long).mean() 
        df["MACD"]=df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
        df["MACD_signal"]=df["MACD"].ewm(span=macd_signal).mean() 
        df["MACD_oscillator"]=df.apply(lambda x:(x["MACD"]-x["MACD_signal"]), axis=1)

        # df[["MACD","MACD_signal"]].plot.line(subplots=False)

        self.MACD = df['MACD'].iloc[-1]
        self.MACD_signal = df['MACD_signal'].iloc[-1]
""" 
        self.state = STAY
        df["MACD_1칸전"] = df["MACD"].shift(1)
        df["MACD_signal_1칸전"] = df["MACD_signal"].shift(1)
        df['MACD_state']=df.apply(lambda x: 1 if (x["MACD"]>=x["MACD_signal"] and x["MACD_1칸전"]<x["MACD_signal_1칸전"]) \
                                            else (-1 if (x["MACD"]<=x["MACD_signal"] and x["MACD_1칸전"]>x["MACD_signal_1칸전"]) \
                                            else 0), axis = 1)
        df['MACD>signal'] = df.apply(lambda x: 1 if (x['MACD']>x['MACD_signal']) \
                                                else (0 if(x['MACD']<=x['MACD_signal']) \
                                                else -999), axis=1 )
       """                                              
class  RelativeStrengthIndex:
    #MACD : 단기(12일) 지수이평선 - 장기(26일) 지수이평선
    #signal : 9일의 MACD 지수이평선
    #oscillator : MACD - signal
    def __init__(self, df) -> None:
        # 상승, 하락분을 알기위해 현재 종가에서 전일 종가를 빼서 데이터프레임에 추가하겠습니다.
        RSI_n = 14

        df["delta"]=df['close'].diff()

        # U(up): n일 동안의 종가 상승 분
        df["RSI_U"]=df["delta"].apply(lambda x: x if x>0 else 0)
        
        # D(down): n일 동안의 종가 하락 분 --> 음수를 양수로 바꿔줌
        df["RSI_D"]=df["delta"].apply(lambda x: x * (-1) if x<0 else 0)
        
        # AU(average ups): U값의 평균
        df["RSI_AU"]=df["RSI_U"].ewm(com=(RSI_n - 1), min_periods=RSI_n).mean()
        
        # DU(average downs): D값의 평균
        df["RSI_AD"]=df["RSI_D"].ewm(com=(RSI_n - 1), min_periods=RSI_n).mean()

        df["RSI"] = df.apply(lambda x:x["RSI_AU"]/(x["RSI_AU"]+ x["RSI_AD"]) * 100, axis=1)

        df['RSI_>50'] = df.apply(lambda x: 2 if (x['RSI']>70) \
                                            else (1 if (x['RSI']>50) \
                                            else (0 if(x['RSI']>30)
                                            else (-1 if(x['RSI']>0)
                                            else -999))) , axis=1)

        # df[["RSI"]].plot.line(subplots=False)

        self.RSI = df["RSI"].iloc[-1]
        # plt.axhline(70)
        # plt.axhline(30)


class Indicator:
    def __init__(self, _ticker, _interval = 'minute5', _count = 300) -> None:
        self.df = pyupbit.get_ohlcv(ticker=_ticker, interval=_interval, count=_count)

        self.indi_RSI = RelativeStrengthIndex(self.df)
        self.indi_MACD = MovingAvgConvDiv(self.df)
        self.indi_BOL = BollingerBands(self.df)
        #self.MA10 = MovingAverage(self.df, 60)
    


if __name__ == "__main__":

    a = Indicator(_ticker='KRW-BTC', _interval = 'minute5', _count = 50)
    # with pd.option_context('display.max_rows', None):  
    print(a.df[['MACD','MACD_signal','MACD>signal',"RSI", 'RSI>50']])
    print(type(a.df['RSI>50'].iloc[-1]))
    # print(a.df)

    # print('lbb',a.BB.lbb)
    # print('ubb',a.BB.ubb)

    #plt.show()
    
