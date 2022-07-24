


from numpy import NaN


def MACD_RSI_strategy(df):
    """
    매수조건
    ㅇ MACD>MACD_signal && 50<RSI<70 &&  

    매도조건
    ㅇ MACD<MACD_signal → 매수량의 100% 매도
    ㅇ state==walkingOnBB && close<BB_ubb → 보유량의 50% 매도
    """
    df['order_type'] = NaN
    df['order_rate'] = NaN
    for i in range(len(df.index)):
        if (df.iloc[i]['MACD']>df.iloc[i]['MACD_signal']) & (50<df.iloc[i]['RSI']) & (df.iloc[i]['RSI']<70):
            df.iloc[i]['order_type'] = 'buy'
            df.iloc[i]['order_rate'] = 1
        elif df.iloc[i]['MACD']<df.iloc[i]['MACD_signal']:
            df.iloc[i]['order_type'] = 'sell'
            df.iloc[i]['order_rate'] = 1
        elif (df.iloc[i]['BB_walking'] == True) & (df.iloc[i]['close']<df.iloc[i]['BB_ubb']):
            df.iloc[i]['order_type'] = 'sell'
            df.iloc[i]['order_rate'] = 0.5
        