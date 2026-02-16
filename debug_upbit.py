import pyupbit
import datetime

def test_ohlcv(interval, count):
    print(f"Testing interval: {interval}, count: {count}")
    try:
        df = pyupbit.get_ohlcv("KRW-BTC", interval=interval, count=count)
        if df is None:
            print("Result: None")
        elif df.empty:
            print("Result: Empty DataFrame")
        else:
            print(f"Result: Success, Rows: {len(df)}")
            print("Last row:")
            print(df.tail(1))
            # Check for NaN in recent data which would affect indicators
            if len(df) > 50:
                 print("Checking for NaNs in last 50 rows...")
                 print(df.iloc[-50:].isnull().sum())
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_ohlcv("minute1", 300)
    test_ohlcv("minute5", 300)
