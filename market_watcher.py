import pyupbit
import pandas as pd
import time, datetime
import copy

#일봉데이터 받아서 티커별 정리 갱신
#
def value_top10_watcher(dict_tickers, cnt=10):
    dict_tickers_clone = copy.deepcopy(dict_tickers)

    df_value = pd.DataFrame( data = None , index = [] , \
        columns = ['ticker', 'open', 'high', 'low', 'close', 'volume', 'value','value_cumsum'])


    for ticker, df in dict_tickers_clone.items():
        df = df.iloc[-cnt:, :] #cnt개 만 남기기
        df['value_cumsum'] = df['value'].cumsum()
        df_value.loc[len(df_value)] = [ ticker, \
                            df['open'].iloc[-1],\
                            df['high'].iloc[-1],\
                            df['low'].iloc[-1], \
                            df['close'].iloc[-1], \
                            df['volume'].iloc[-1],\
                            df['value'].iloc[-1],\
                            df['value_cumsum'].iloc[-1]
                                                ] 
        df_value.sort_values('value_cumsum',ascending=False,inplace=True,ignore_index=True)
    
    list_value_top10 = df_value.loc[0:9,'ticker'].values.tolist()
    dict_value_top10 = {}
    for ticker in list_value_top10:
        dict_value_top10[ticker] = dict_tickers[ticker]

    return list_value_top10, dict_value_top10

def value_watcher(_interval, _count):
    print('*** '+_interval+'구간 '+str(_count)+'개 거래량 상위 코인 조회중 ***')
    df_value = pd.DataFrame( data = None , index = [] , \
        columns = ['ticker', 'open', 'high', 'low', 'close', 'volume', 'value','value_cumsum'])

    # 전종목 데이터 수집
    tickers = pyupbit.get_tickers(fiat="KRW")

    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, interval=_interval, count=_count)
        df['value_cumsum'] = df['value'].cumsum() # 거래량 누적합
        df_value.loc[len(df_value)] = [ ticker, \
                            df['open'].iloc[-1],\
                            df['high'].iloc[-1],\
                            df['low'].iloc[-1], \
                            df['close'].iloc[-1], \
                            df['volume'].iloc[-1],\
                            df['value'].iloc[-1],\
                            df['value_cumsum'].iloc[-1]
                                                ] 
        df_value.sort_values('value_cumsum',ascending=False,inplace=True,ignore_index=True)
    
        # print(df_value)
        time.sleep(0.1)


    value_top10 = df_value.loc[0:9,'ticker'].values.tolist()

    return value_top10, df_value


def market_watcher(dict_tickers):
    list_value_top10, dict_value_top10 = value_top10_watcher(dict_tickers, cnt=10)

    return dict_value_top10

if __name__ == "__main__":
    try:
        while(1):
            value_top10, df_val = value_watcher(_interval = 'minute10', _count = 10)
            print('value_top10')
            print(datetime.datetime.now())
            print(value_top10)
            print(df_val)
            print()

    except Exception as e:
        print("에러:",e)

