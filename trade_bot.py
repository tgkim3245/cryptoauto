from timer import *
from wallet import *
from indicators_class import *
from market_watcher import value_watcher
import copy

timedelay = datetime.datetime.now()

def find_fascinating_coins(interval, cnt):
    fascinating_coins = []

    fascinating_coins = value_watcher(_interval=interval, _count=cnt)


    return fascinating_coins



'''
#매수조건
거래량 top10
~매도한지10분 && macd>signal && 70>RSI>50 && 현재가>BOL mbb &&

#매수량
비트코인 100%
'''
def buy_bot(ticker):
    global timedelay

    indicator = Indicator(_ticker=ticker, _interval='minute10', _count=100)
    if (indicator.df['MACD>signal'].iloc[-1] == 1) and (indicator.df['RSI>50'].iloc[-1] == 1) and (timedelay<datetime.datetime.now()) :
        buy_market(ticker, percent=0.01)
        timedelay = datetime.datetime.now() + datetime.timedelta(minutes=10)
        print('구매 : ', ticker, '시간 : ', timeNow())
        print('')



'''
#매도조건
~매수한지10분
100% 
    -3% 돌파시 || macd<signal 
50%
    10% 수익률 돌파시 , RSI 70 하향돌파시, 볼린저밴드 하향돌파 음봉시
    
'''
def sell_bot(ticker):
    global timedelay

    indicator = Indicator(_ticker=ticker, _interval='minute10', _count=100)
    if():
        pass
    elif (indicator.df['MACD>signal'].iloc[-1] == 0) and (indicator.df['RSI>50'].iloc[-1] == 1) and (timedelay<datetime.datetime.now()):
        sell_market(ticker, percent = 0.5)
        timedelay = datetime.datetime.now() + datetime.timedelta(minutes=10)
        print('매도 : ', ticker, '시간 : ', timeNow())
        print('')



if __name__ == "__main__":
    main_timer = TIMER()
    serching_timer = TIMER()

    fascinating_coins = ['KRW-BTC' for _ in range(10)]
    while True:
        main_timer.start()

        try:
            serching_timer.start()
            fascinating_coins = find_fascinating_coins(interval='minute1', cnt = 10)
            print('fascinating_coins : ',fascinating_coins)
            serching_timer.stop(print_result=True, name='serching_time')



            for ticker in fascinating_coins:
                buy_bot(ticker)
                #pass

            for ticker in coins_in_wallet():
                sell_bot(ticker)
                #pass


            time.sleep(1)
        except Exception as e:
            print("오류발생:",e)
            time.sleep(10)

        main_timer.stop(print_result=True, name='main_loop_time')
