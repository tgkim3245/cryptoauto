from preprocessing_dict_tickers import * 
from backtest import * 
from strategy import *
from market_watcher import market_watcher

if __name__ == "__main__":

    while(1):
        dict_tickers = refresh_dict_tickers(_interval="minute1", _count=100)

        dict_watching_coins = market_watcher(dict_tickers) #거래액상위코인, 보유코인, 매도/매수주문코인 등

        preprocessing_dict_tickers(dict_watching_coins) #추가할거 싸악 해주고

        # backtest(dict_watching_coins,MACD_RSI_strategy)

        ...


