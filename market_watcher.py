import pyupbit
import pandas as pd
import time, datetime

#일봉데이터 받아서 티커별 정리 갱신
#

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


if __name__ == "__main__":
    try:
        while(1):
            value_top10, df_val = value_watcher(_interval = 'minute1', _count = 10)
            print('value_top10')
            print(datetime.datetime.now())
            print(value_top10)
            print(df_val)
            print()

    except Exception as e:
        print("에러:",e)

