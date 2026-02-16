import sqlite3
import pandas as pd
import datetime
import os
from contextlib import contextmanager

# 현재 파일(database.py)이 위치한 디렉토리를 기준으로 DB 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "cryptoauto.db")

@contextmanager
def get_connection():
    """DB 연결 컨텍스트 매니저"""
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """데이터베이스 테이블 초기화"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. 시장 데이터 테이블 (OHLCV)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                ticker TEXT,
                interval TEXT,
                time TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                PRIMARY KEY (ticker, interval, time)
            )
        ''')
        
        # 2. 거래 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT,
                ticker TEXT,
                type TEXT, -- 'buy' or 'sell'
                price REAL,
                amount REAL,
                total_value REAL,
                reason TEXT
            )
        ''')
        
        # 3. 시스템 상태 테이블 (Key-Value)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        ''')
        conn.commit()
    print(f"Database initialized: {DB_FILE}")

def save_ohlcv(df, ticker, interval):
    """OHLCV 데이터 저장 (중복 시 무시)"""
    if df is None or df.empty:
        return
        
    try:
        # DataFrame을 튜플 리스트로 변환
        data = []
        for index, row in df.iterrows():
            time_str = index.strftime("%Y-%m-%dT%H:%M:%S") if isinstance(index, pd.Timestamp) else str(index)
            data.append((
                ticker, 
                interval, 
                time_str,
                float(row['open']), 
                float(row['high']), 
                float(row['low']), 
                float(row['close']), 
                float(row['volume'])
            ))
            
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO market_data (ticker, interval, time, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()
            
        print(f"DB: Saved {len(data)} rows for {ticker} ({interval})")
    except Exception as e:
        print(f"DB Save Error: {e}")
        # import traceback; traceback.print_exc()

def load_ohlcv(ticker, interval, start=None, end=None, limit=None):
    """OHLCV 데이터 조회"""
    query = "SELECT * FROM market_data WHERE ticker = ? AND interval = ?"
    params = [ticker, interval]
    
    if start:
        query += " AND time >= ?"
        params.append(start)
    if end:
        query += " AND time <= ?"
        params.append(end)
        
    query += " ORDER BY time ASC"
    
    if limit:
        query += f" LIMIT {limit}"
        
    try:
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            
        if not df.empty:
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
            cols = ['open', 'high', 'low', 'close', 'volume']
            df = df[cols].astype(float)
        return df
    except Exception as e:
        print(f"DB Load Error: {e}")
        return None

def log_trade(ticker, side, price, amount, reason=""):
    """거래 기록 저장"""
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_value = price * amount
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trade_history (time, ticker, type, price, amount, total_value, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (time_str, ticker, side, price, amount, total_value, reason))
        conn.commit()

def get_trade_history(limit=50):
    """최근 거래 기록 조회"""
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM trade_history ORDER BY id DESC LIMIT ?", conn, params=[limit])
        return df
    except Exception as e:
        print(f"DB Trade History Load Error: {e}")
        return pd.DataFrame()

def save_state(key, value):
    """시스템 상태 저장"""
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO system_state (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (str(key), str(value), time_str))
        conn.commit()

def load_state(key):
    """시스템 상태 조회"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM system_state WHERE key = ?", (str(key),))
        row = cursor.fetchone()
    return row[0] if row else None

# 모듈 로드 시 DB가 없으면 초기화
if not os.path.exists(DB_FILE):
    init_db()
