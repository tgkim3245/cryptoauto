import os
import sys
import pyupbit
from dotenv import load_dotenv

# UTF-8 출력 설정 (윈도우 환경 대응)
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# .env 파일 로드
load_dotenv()

access = os.getenv("UPBIT_ACCESS_KEY")
secret = os.getenv("UPBIT_SECRET_KEY")

try:
    upbit = pyupbit.Upbit(access, secret)
    balances = upbit.get_balances()
    
    if balances is not None and not isinstance(balances, str):
        print("Success: API Connection Verified!")
        print("--- Account Balance ---")
        for b in balances:
            print(f"Currency: {b['currency']}, Balance: {b['balance']}, Avg Buy: {b['avg_buy_price']}")
    else:
        print(f"Error: API Connection Failed. Check your keys. Response: {balances}")
except Exception as e:
    print(f"Exception Occurred: {e}")
