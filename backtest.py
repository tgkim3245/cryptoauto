from preprocessing_dict_tickers import * 
from backtest import * 
from strategy import *
from market_watcher import market_watcher
import pprint
import copy

""" 
백테스트 전용
"""
def calc_ror(df):
    #매수 매도를 하나씩만 남김
    df['ror'] = 1
    state = '미보유'
    buy_time = NaN
    cash = 1
    coin = 0
    buy_count = 0
    for i in range(len(df.index)):
        if (i==len(df.index)-1) & (state=='보유'):
            df.iloc[i]['order_type'] = 'sell'
            df.iloc[i]['order_rate'] = 1

        if df.iloc[i]['order_type'] == 'buy':
            if state =='미보유':
                state = '보유'
                buy_time = df.index[i]
                coin = cash
                cash = 0
                buy_count = buy_count +1
            elif state == '보유':
                df.iloc[i]['order_type'] = ''

        elif df.iloc[i]['order_type'] == 'sell':
            if state =='미보유':
                df.iloc[i]['order_type'] = ''
            elif state == '보유':
                if df.iloc[i]['order_rate'] == 1:
                    state = '미보유'
                df.iloc[i,df.index.index('ror')] = df.iloc[i]['close'] / df[buy_time,'high']
                cash = cash + df.iloc[i]['close'] / df[buy_time,'high'] * coin * df.iloc[i]['order_rate']
                coin = coin - df.iloc[i]['close'] / df[buy_time,'high'] * coin * df.iloc[i]['order_rate']
    
    return cash, buy_count

    #마지막을 매도로 끝냄
    #

def backtest(dict_tickers, func_strategy):

    for ticker, df in dict_tickers.items():
        df_clone = df.copy() #원본 df 훼손 방지 복사

        func_strategy(df_clone)           #매수/매도 전략 시행

        hpr,buy_count = calc_ror(df_clone)            #장부작성 및 수익률 계산

        print(ticker, hpr*100,'%', buy_count,'번 매수')
        # print(df['order_type1'])
        
        

if __name__ == "__main__":
    # df1 = pd.DataFrame({'a':['a0','a1','a2','a3'],
    #             'b':['b0','b1','b2','b3'],
    #             'c':['c0','c1','c2','c3']},
    #             index = [5,6,7,8])
    # print(df1)
    # print(df1.iloc[2]['b'])

    # df2 = pd.DataFrame({'a':['na2','na3','na4','na5'],
    #                 'b':['nb2','nb3','nb4','nb5'],
    #                 'c':['nc2','nc3','nc4','nc5']},
    #                 index = [8,9,10,11])

    # dict1 = {'a':1,'b':2,'c':3,'d':4,'e':5}
    # l = ['a','d']
    # print(dict1)
    # # del(dict1[l])
    # dict1.pop(l)
    # print(dict1)

    # dict_tickers = refresh_dict_tickers(_interval="minute1", _count=100)
    # dict_watching_coins = market_watcher(dict_tickers) #거래액상위코인, 보유코인, 매도/매수주문코인 등
    
    dict_watching_coins = {'KRW-BTC':pyupbit.get_ohlcv('KRW-BTC', interval='minute10', count=500)}
    preprocessing_dict_tickers(dict_watching_coins) #추가할거 싸악 해주고
    backtest(dict_watching_coins,MACD_RSI_strategy)
    