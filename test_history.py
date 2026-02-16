import requests
import time

def test_history_fetch():
    ticker = "KRW-BTC"
    interval = "1" # minute1
    url = f"https://api.upbit.com/v1/candles/minutes/{interval}"
    
    # 1. Get latest data
    print("Fetching latest data...")
    params = {"market": ticker, "count": 200}
    response = requests.get(url, params=params)
    data = response.json()
    
    if len(data) == 0:
        print("Failed to fetch latest data.")
        return

    first_candle = data[-1] # Oldest in response
    last_candle = data[0]   # Newest in response
    print(f"Latest chunk: {len(data)} candles, {first_candle['candle_date_time_kst']} ~ {last_candle['candle_date_time_kst']}")
    
    # 2. Loop to fetch past data
    current_to = first_candle['candle_date_time_kst'] # String format: '2024-01-01T00:00:00'
    # Upbit API expects 'to' in format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-ddTHH:mm:ss'
    
    for i in range(5):
        print(f"\nFetching data before {current_to}...")
        # Try adding KST offset
        to_param = current_to + "+09:00"
        params = {"market": ticker, "to": to_param, "count": 200}
        
        # Prepare request to print URL
        req = requests.Request('GET', url, params=params)
        prepped = req.prepare()
        print(f"Request URL: {prepped.url}")
        
        session = requests.Session()
        response = session.send(prepped)
        data = response.json()
        
        if len(data) == 0:
            print(f"Stopped fetching at iteration {i}. No more data returned.")
            break
            
        first_candle = data[-1]
        last_candle = data[0]
        print(f"Chunk {i+1}: {len(data)} candles, {first_candle['candle_date_time_rst'] if 'candle_date_time_rst' in first_candle else first_candle['candle_date_time_kst']} ~ {last_candle['candle_date_time_kst']}")
        current_to = first_candle['candle_date_time_kst']
        time.sleep(0.5)

if __name__ == "__main__":
    test_history_fetch()
