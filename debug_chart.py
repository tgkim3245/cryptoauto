import sys
import pyupbit
import pandas as pd
import datetime

# UTF-8 출력 설정
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    print("1. Upbit API Fetching...")
    df = pyupbit.get_ohlcv("KRW-BTC", interval="minute1", count=5)
    
    if df is None:
        print("Error: API Fetch Failed (df is None)")
    else:
        print("Success: API Fetched")
        print(df.head())
        
        print("\n2. Indicators Calculation Test...")
        df['ma5'] = df['close'].rolling(window=5).mean()
        print("MA5 Calculated")
        
        print("\n3. JSON Conversion Test...")
        result = []
        for i in range(len(df)):
            row = df.iloc[i]
            item = {
                "time": int(df.index[i].timestamp()),
                "open": float(row['open']),
                "close": float(row['close'])
            }
            result.append(item)
            print(f"Converted: {item}")

except Exception as e:
    print(f"Exception: {e}")
