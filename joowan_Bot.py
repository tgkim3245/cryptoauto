from wallet import *
from indicators_class import *


'''
(매수조건)  MA5일선 위에서 양봉이 하나뜨면, 다음날 아침 (나스닥 상승, 채결강도>150%, 외인보유율 증가) 세가지 조건이 맞으면 시초가 매수

(매도조건)  MA5일선 아래로 음봉 2개 연속뜨면 무조건 매도
            3%먹으면 무조건 매도
'''

#최근 x일 동안 하루 중 가장 가격이 높았던 시간을 찾아줌 (0~23시) 
def find_sell_hour(days=5):
    df = pyupbit.get_ohlcv('KRW-BTC', interval='minute60', count=24*days)
    #print(df['close'])

    list_sum = [0 for i in range(24)]

    for idx in df.index:
        list_sum[idx.hour] += df.loc[idx,'close']
        
    #print(list_sum)
    print(list_sum.index(max(list_sum)))

    #return bestTime


if __name__ == '__main__':
    df = pyupbit.get_ohlcv('KRW-BTC', interval='day', count=200)

    ma5 = MovingAverage(df,5)
    ma10 = MovingAverage(df,10)

    #print(df)
    


    find_sell_hour(10)




'''
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print("오류발생:",e)
        time.sleep(10)
'''