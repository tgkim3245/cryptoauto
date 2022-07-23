import pyupbit
from pprint import pprint

#주문요청에는 요청수 제한이 있으니 고려할것
#https://docs.upbit.com/docs/user-request-guide

class WALLET:
    def __init__(self) -> None:
        self.access = "xBxGbQqMSofSPpU1768sxYXp3qyYI7Ywexm6ze1e"
        self.secret = "TWo8dWfz1CGItcsfW0hNyOxQzb9Qbwia0O6QFF6z"
        self.my = pyupbit.Upbit(self.access, self.secret)  

    def fee(self,price):
        fee = 0.0005*price
        return fee
    
    def get_my_cash(self): #계좌 보유 현금 조회
        cash = self.my.get_balance("KRW")
        return cash

    # def get_my_total(self): #총매수금액
    #     myCoin = self.my.get_amount('ALL')
    #     return myCoin

    def get_list_my_coin(self): #보유중인 코인 리스트 리턴
        my_coins_list = []
        for i in range(len(self.my.get_balances())):
            if self.my.get_balances()[i]['currency']=='KRW':
                continue
            my_coins_list.append('KRW-' + self.my.get_balances()[i]['currency'])
        return my_coins_list

    # 호가단위가 있는데 어떻게 적용?
    # https://docs.upbit.com/docs/market-info-trade-price-detail
    # def buy_market(self, ticker, percent=0.01):
    #     money = my.get_balance("KRW")
    #     my.buy_market_order(ticker, money*percent)


    # def sell_market(self., ticker, percent = 0.5):
    #     amount = my.get_balance(ticker) 
    #     cur_price = pyupbit.get_current_price(ticker) 
    #     total = amount * cur_price 
    #     my.sell_market_order(ticker, amount * percent)
        
    #매수매도기록
    #잔고확인


wallet=WALLET()


if __name__ == "__main__":
    # pprint.pprint(my.get_chance('KRW-XRP'))
    #pprint(my.get_balances())
    # print(my.get_balance('KRW-IOTA'))
    # print(len(my.get_balances()))
    # print(coins_in_wallet())
    # pprint(my.get_order("KRW-EOS", state="done"))
    # tickers=pyupbit.get_tickers(fiat="KRW")
    # print(tickers)
    # buy_market('KRW-STPT')
    # print(coins_in_wallet())
    # sell_market('KRW-IOTA')
    # print(wallet.get_my_cash())
    print(wallet.get_list_my_coin())
    # pprint(wallet.my.get_balances())
