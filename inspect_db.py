import sqlite3
import os
import pandas as pd

DB_FILE = "cryptoauto.db"

def get_file_size(file_path):
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
    return "File not found"

def inspect_db():
    print("="*50)
    print(f"DB File: {DB_FILE}")
    print(f"Total Disk Usage: {get_file_size(DB_FILE)}")
    print("="*50)
    
    if not os.path.exists(DB_FILE):
        print("Error: Database file not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    
    tables = ['market_data', 'trade_history', 'system_state']
    
    for table in tables:
        print(f"\n[ Table: {table} ]")
        try:
            # 개수 확인
            count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table}", conn).iloc[0]['cnt']
            print(f"Total Rows: {count}")
            
            # 최근 데이터 5개 보기
            if count > 0:
                limit = 5
                df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT {limit}", conn)
                print(df)
            else:
                print("Table is empty.")
        except Exception as e:
            print(f"Error inspecting table {table}: {e}")
            
    conn.close()
    print("\n" + "="*50)

if __name__ == "__main__":
    inspect_db()
