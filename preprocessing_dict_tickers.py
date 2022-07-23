from cmath import nan
from numpy import NaN
import pyupbit
import pandas as pd
import json
import telegram_message as t
import time, datetime
from dateutil.relativedelta import relativedelta
from json_file_convert import * 
from indicator import *


def get_cnt_refresh(interval, last_timestamp):
    """
    리프레시할 갯수(cnt)를 계산
    :param interval:
    :return: 날짜의 차이+1 (올림)을 해줘서 마지막 값은 무조건 리프레시 되게 작동
    """
    timedelta = datetime.datetime.now() - last_timestamp

    if interval in ["day", "days"]:
        cnt = timedelta//datetime.timedelta(days=1) 
    elif interval in ["minute1", "minutes1"]:
        cnt = timedelta//datetime.timedelta(minutes=1) 
    elif interval in ["minute3", "minutes3"]:
        cnt = timedelta//datetime.timedelta(minutes=3) 
    elif interval in ["minute5", "minutes5"]:
        cnt = timedelta//datetime.timedelta(minutes=5) 
    elif interval in ["minute10", "minutes10"]:
        cnt = timedelta//datetime.timedelta(minutes=10)
    elif interval in ["minute15", "minutes15"]:
        cnt = timedelta//datetime.timedelta(minutes=15) 
    elif interval in ["minute30", "minutes30"]:
        cnt = timedelta//datetime.timedelta(minutes=30) 
    elif interval in ["minute60", "minutes60"]:
        cnt = timedelta//datetime.timedelta(minutes=60) 
    elif interval in ["minute240", "minutes240"]:
        cnt = timedelta//datetime.timedelta(minutes=240) 
    elif interval in ["week",  "weeks"]:
        cnt = timedelta//datetime.timedelta(weeks=1)
    elif interval in ["month", "months"]:
        delta = relativedelta(datetime.datetime.now(), last_timestamp)
        res_months = delta.months + (delta.years * 12)
        cnt = res_months
    else:
        cnt = timedelta//datetime.timedelta(days=1) 

    return cnt +1

def refresh_dict_tickers(dict_tickers, _interval="day", _count=10, _fiat="KRW"):  
    '''
    마켓의 모든 ticker를 df으로 일정갯수로 저장/갱신
    '''
    tickers_list = pyupbit.get_tickers(fiat=_fiat)
    # tickers_list = ['KRW-BTC','KRW-ETH']
       
    for ticker in tickers_list:
        if ticker in dict_tickers: #기존목록에 있으면
            cnt = get_cnt_refresh(_interval, dict_tickers[ticker].index[-1]) #몇개를 불러와야하는지 구해서
            if cnt > _count or cnt+len(dict_tickers[ticker].index) < _count : #불러온 dict_tickers 가 너무 옛날자료 라면 or 새로채우는게 맞으면
                del(dict_tickers[ticker]) #있던거 지우고
                dict_tickers[ticker] = pyupbit.get_ohlcv(ticker, interval=_interval, count=_count)
            else:
                df = pyupbit.get_ohlcv(ticker, interval=_interval, count=cnt) #구한갯수만큼 불러와서
                dict_tickers[ticker] = pd.concat([dict_tickers[ticker], df]) #기존거랑 합치기
                dict_tickers[ticker] = dict_tickers[ticker].loc[~dict_tickers[ticker].index.duplicated(keep='last')] #합치고 index가 같은 건 df(최신)걸로 남기고 중복제거
                dict_tickers[ticker] = dict_tickers[ticker].iloc[-_count:, :] #행의 갯수를 _count만큼만 남기고 위에서 부터 삭제 
        else:  #새로운 코인 or 처음 실행
            dict_tickers[ticker] = pyupbit.get_ohlcv(ticker, interval=_interval, count=_count)
        
        print('현재',ticker, '갱신완료', tickers_list.index(ticker)/len(tickers_list)*100,'% 진행중')
        time.sleep(0.1)


#모든 ticker의 ohlcv 갱신
def preprocessing_dict_tickers(dict_tickers, _interval="day", _count=10, _fiat="KRW"): 
    """ 
    ohlcv 갱신후
    indicator 추가
    """ 

    refresh_dict_tickers(dict_tickers, _interval, _count, _fiat)
    
    for ticker, df in dict_tickers.items():
        df['state'] = NaN #sell buy 등 매수/매도 명령
        BollingerBands(df)
        MovingAverage(df,span=10)
        MovingAverage(df,span=30)
        MovingAvgConvDiv(df)
        RelativeStrengthIndex(df)




if __name__ == "__main__":
    # mydict = {}
    # mydict = json_to_dict_tickers('min1_10_220721_214435')
    # print(mydict)
    # preprocessing_dict_tickers(mydict,'minute1',100)
    # print(mydict)

    # drawing_plot(mydict['KRW-BTC'],'candle','volume','MA10','MA30','BB','RSI','MACD')
    
    # print(mydict)
    # dict_tickers_to_json(mydict,'min1_100')
    # print(mydict)

    # time.sleep(60*5)
    # refresh_dict_tickers(mydict,'minute1',10)
    # print(mydict)



    # df = pyupbit.get_ohlcv('KRW-BTC',interval='month', count=50)
    # df = pd.DataFrame()
    # refresh_df_tickers(df)
    # print(df)
    # td = datetime.datetime.now() - df.index[-1]
    # print(df)
    # print(td)
    # print((td)//datetime.timedelta(days=1)+1)
    # print(type(datetime.datetime.now()- df.index[-4]))
    # print('차이',(datetime.datetime.now().to_period('M').astype(int)- df.index[-20].to_period('M').astype(int)))
    
    
    # print(datetime.datetime.now())
    # i = -20
    # print(df.index[i])
    # delta = relativedelta(datetime.datetime.now(), df.index[i])
    # res_months = delta.months + (delta.years * 12)
    # print(res_months+1)

    # dicc = {}
    # # refresh_dict_tickers(dicc)
    # dicc['a'] = 'd'
    # dicc['b'] = 1
    # print(dicc['b'])
    # print('a'in dicc)
    # print('d'in dicc)
    
    df1 = pd.DataFrame({'a':['a0','a1','a2','a3'],
                   'b':['b0','b1','b2','b3'],
                   'c':['c0','c1','c2','c3']},
                  index = [5,6,7,8])

    df2 = pd.DataFrame({'a':['na2','na3','na4','na5'],
                    'b':['nb2','nb3','nb4','nb5'],
                    'c':['nc2','nc3','nc4','nc5']},
                    index = [8,9,10,11])
    df1['state'] = NaN
    print(df1)



