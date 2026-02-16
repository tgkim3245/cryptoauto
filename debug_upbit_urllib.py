import urllib.request
import json
import ssl

def check_upbit_api(market="KRW-BTC", interval="minutes/5", count=200):
    url = f"https://api.upbit.com/v1/candles/{interval}?market={market}&count={count}"
    print(f"Requesting: {url}")
    try:
        # SSL context bypass for simple test
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"Status: {response.status}")
                print(f"Data length: {len(data)}")
                if len(data) > 0:
                    print("First candle:", data[0])
                    print("Last candle:", data[-1])
                else:
                    print("Data is empty!")
            else:
                print(f"Error: {response.status}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_upbit_api()
