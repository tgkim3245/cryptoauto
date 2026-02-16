import database as db
import pandas as pd
import datetime
import os
from backtest import get_backtest_result

def test_database_module():
    print("Testing database module...")
    
    # 1. OHLCV 저장/조회 테스트
    ticker = "TEST-BTC"
    interval = "day"
    now = datetime.datetime.now()
    
    data = {
        'open': [100, 110],
        'high': [120, 130],
        'low': [90, 100],
        'close': [110, 120],
        'volume': [10, 20]
    }
    index = [now - datetime.timedelta(days=1), now]
    df = pd.DataFrame(data, index=index)
    
    print("Saving test data...")
    db.save_ohlcv(df, ticker, interval)
    
    print("Loading test data...")
    loaded_df = db.load_ohlcv(ticker, interval)
    
    if loaded_df is not None and len(loaded_df) >= 2:
        print(">> OHLCV Test: PASS")
    else:
        print(">> OHLCV Test: FAIL")
        
    # 2. 상태 저장/조회 테스트
    print("Testing state storage...")
    db.save_state("test_key", "test_value")
    loaded_value = db.load_state("test_key")
    
    if loaded_value == "test_value":
        print(">> State Test: PASS")
    else:
        print(f">> State Test: FAIL (Expected 'test_value', got '{loaded_value}')")

def test_backtest_integration():
    print("\nTesting backtest integration...")
    # 실제 API 호출이 발생할 수 있음
    try:
        result = get_backtest_result(period=5, k=0.5)
        if "error" in result:
             print(f">> Backtest Test: FAIL ({result['error']})")
        else:
             print(f">> Backtest Test: PASS (Return: {result['total_return']}%)")
    except Exception as e:
        print(f">> Backtest Test: ERROR ({e})")

if __name__ == "__main__":
    if os.path.exists("cryptoauto.db"):
        print("DB file exists.")
    test_database_module()
    test_backtest_integration()
