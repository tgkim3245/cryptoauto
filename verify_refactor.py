import requests
import time
import sqlite3
import pandas as pd
import os

BASE_URL = "http://localhost:8000"
DB_FILE = r"c:\Users\TaeGon_laptop\Desktop\cryptoauto\cryptoauto.db"

def check_db_count(interval):
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM market_data WHERE interval=?", (interval,))
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()

def test_api_caching():
    interval = "minute5"
    print(f"--- Testing {interval} ---")
    
    # Initial DB count
    cnt1 = check_db_count(interval)
    print(f"Initial DB Count: {cnt1}")
    
    # 1st Request
    start = time.time()
    resp = requests.get(f"{BASE_URL}/api/ohlcv?interval={interval}&count=200")
    print(f"1st Request Status: {resp.status_code}, Time: {time.time() - start:.2f}s")
    
    cnt2 = check_db_count(interval)
    print(f"DB Count after 1st req: {cnt2}")
    
    # 2nd Request (Should be fast and skip API)
    start = time.time()
    resp = requests.get(f"{BASE_URL}/api/ohlcv?interval={interval}&count=200")
    print(f"2nd Request Status: {resp.status_code}, Time: {time.time() - start:.2f}s")
    
    cnt3 = check_db_count(interval)
    print(f"DB Count after 2nd req: {cnt3}")
    
    if cnt3 == cnt2:
        print("PASS: DB count stable (likely used cache)")
    else:
        print("NOTE: DB count changed (merged new data?)")

if __name__ == "__main__":
    test_api_caching()
