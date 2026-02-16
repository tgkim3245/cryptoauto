import os
import time
import threading
import datetime
import pyupbit
import requests
import pandas as pd
import asyncio
from backtest import get_backtest_result
from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import database as db
import json
import indicators as ind
import traceback
import indicators as ind
import traceback

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 글로벌 설정
TARGET_TICKER = "KRW-BTC"
SLIPPAGE = 0.0005 # 0.05%

# 글로벌 상태 관리
state = {
    "is_running": False,
    "btc_price": 0,
    "total_krw": 0,
    "btc_balance": 0,
    "target_price": 0,
    "current_strategy": "변동성 돌파",
    "logs": ["서버가 시작되었습니다."]
}

access = os.getenv("UPBIT_ACCESS_KEY")
secret = os.getenv("UPBIT_SECRET_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

upbit = pyupbit.Upbit(access, secret)

def send_telegram_message(message):
    """텔레그램 메시지 전송"""
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        params = {"chat_id": telegram_chat_id, "text": message}
        requests.get(url, params=params, timeout=5)
    except Exception as e:
        add_log(f"텔레그램 전송 실패: {e}")

def add_log(message):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    state["logs"].append(formatted_msg)
    if len(state["logs"]) > 50: # 로그 버퍼 증량
        state["logs"].pop(0)
    print(formatted_msg)

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
        return target_price
    except Exception:
        return 0

def get_start_time(ticker):
    """시작 시간 조회 (오전 9시)"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def trading_logic():
    """자동매매 핵심 로직 (변동성 돌파 전략)"""
    ticker = TARGET_TICKER
    k = 0.5 # 변동성 계수
    
    strategy_name = state.get("current_strategy", "변동성 돌파")
    add_log(f"{ticker} 자동매매 로직 가동 중... (전략: {strategy_name})")
    
    # 시작 시점 목표가 계산 또는 복구
    saved_target = db.load_state("target_price")
    if saved_target:
        state["target_price"] = float(saved_target)
        add_log(f"저장된 매수 목표가 복구: {state['target_price']} KRW")
    else:
        state["target_price"] = get_target_price(ticker, k)
        db.save_state("target_price", state["target_price"])
        add_log(f"최초 매수 목표가: {state['target_price']} KRW")

    while state["is_running"]:
        try:
            now = datetime.datetime.now()
            # API 호출 최소화를 위해 start_time은 필요할 때만 갱신하거나 캐싱 고려 가능
            # 여기서는 로직 단순화를 위해 유지하되, 예외 처리 보강
            try:
                start_time = get_start_time(ticker)
                end_time = start_time + datetime.timedelta(days=1)
            except:
                time.sleep(1)
                continue

            # 오전 9시 ~ 다음날 오전 8시 59분 50초 사이
            if start_time < now < end_time - datetime.timedelta(seconds=10):
                current_price = pyupbit.get_current_price(ticker)
                state["btc_price"] = current_price
                
                # 매수 조건: 현재가가 목표가 돌파 및 아직 매수 전일 때
                if current_price > state["target_price"]:
                    krw = upbit.get_balance("KRW")
                    if krw > 5000: # 최소 주문 금액 확인
                        # 시장가 매수
                        upbit.buy_market_order(ticker, krw * 0.9995)
                        msg = f"🔔 매수 체결: {ticker}\n매수가: {current_price} KRW\n투자금액: {krw:,.0f} KRW"
                        add_log(msg)
                        send_telegram_message(msg)
                        db.log_trade(ticker, 'buy', current_price, krw / current_price, "Vol Breakout Buy")
                
            else:
                # 오전 8시 59분 50초 ~ 9시 사이: 전량 매도
                btc = upbit.get_balance("BTC")
                if btc > 0.00008: # 최소 수량 확인 (업비트 기준)
                    upbit.sell_market_order(ticker, btc)
                    msg = f"💰 전량 매도 완료 (장마감)\n수량: {btc} BTC"
                    add_log(msg)
                    send_telegram_message(msg)
                    db.log_trade(ticker, 'sell', pyupbit.get_current_price(ticker), btc, "Market Close Sell")
                
                # 다음날 목표가 갱신
                state["target_price"] = get_target_price(ticker, k)
                db.save_state("target_price", state["target_price"])
                add_log(f"새로운 매수 목표가 갱신: {state['target_price']} KRW")
                time.sleep(10) # 9시 정각 중복 실행 방지
            
            # 대시보드 표시용 데이터 갱신 (1초마다)
            time.sleep(1)
            
        except Exception as e:
            add_log(f"매매 로직 오류: {e}")
            time.sleep(1)

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    """메인 페이지: 초기 차트 데이터를 DB에서 미리 로드하여 렌더링"""
    initial_ohlcv = []
    try:
        df = db.load_ohlcv(TARGET_TICKER, "minute5", limit=200)
        if df is not None and not df.empty:
            # indicators.py를 통해 지표 계산 후 전달
            ind.add_all_indicators(df)
            
            # NaN 처리 후 변환
            df = df.where(pd.notnull(df), None)
            
            for index, row in df.iterrows():
                initial_ohlcv.append({
                    "time": int(index.timestamp()),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": float(row['volume']),
                    "ma1": float(row['ma5']) if row['ma5'] else None,
                    "ma2": float(row['ma20']) if row['ma20'] else None,
                    "bb_upper": float(row['bb_upper']) if row['bb_upper'] else None,
                    "bb_lower": float(row['bb_lower']) if row['bb_lower'] else None,
                     "rsi": float(row['rsi']) if row['rsi'] else None,
                     "macd": float(row['macd']) if row['macd'] else None,
                     "macd_signal": float(row['macd_signal']) if row['macd_signal'] else None,
                     "macd_hist": float(row['macd_hist']) if row['macd_hist'] else None
                })
    except Exception as e:
        print(f"초기 데이터 로드 오류: {e}")
        
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "initial_data": json.dumps(initial_ohlcv)
    })

@app.get("/api/status")
async def get_status():
    """상태 조회 API (비동기 처리 강화)"""
    if not state["is_running"]:
        try:
            # API 호출 비용이 있으므로 캐싱 고려 가능하나, 
            # 현재 구조상 상태 갱신 주기를 클라이언트가 제어하므로 
            # 단순 호출로 유지하되 예외 처리만 확실히 함
            state["btc_price"] = pyupbit.get_current_price(TARGET_TICKER) or 0
            state["total_krw"] = upbit.get_balance("KRW") or 0
            state["btc_balance"] = upbit.get_balance("BTC") or 0
        except:
            pass
    return state

async def fetch_ohlcv_data(interval, fetch_count):
    """OHLCV 데이터 페칭 및 DB 동기화 로직 분리"""
    # 1. DB에서 데이터 조회
    df_db = db.load_ohlcv(TARGET_TICKER, interval, limit=fetch_count)
    
    # 2. 최신 데이터 필요 여부 확인
    need_api = True
    if df_db is not None and not df_db.empty:
        last_db_time = df_db.index[-1]
        now = datetime.datetime.now()
        tolerance = datetime.timedelta(seconds=30) if "minute" in interval else datetime.timedelta(hours=1)
        if now - last_db_time < tolerance:
            need_api = False
            # print(f"DEBUG: Using DB data ({interval})")

    # 3. API 호출
    df_api = None
    if need_api:
        try:
            limit = 200
            if fetch_count <= limit:
                df_api = pyupbit.get_ohlcv(TARGET_TICKER, interval=interval, count=fetch_count)
            else:
                # Pagination 로직 간소화
                df_api = pyupbit.get_ohlcv(TARGET_TICKER, interval=interval, count=fetch_count) 
                # pyupbit가 내부적으로 pagination을 완벽히 지원하지 않을 수 있어, 
                # 필요시 추가 구현해야 하나 일단 최대 200개 제한이 있는 경우가 많음.
                # 여기서는 기본적인 호출로 유지.
        except Exception as e:
            print(f"API Fetch Error: {e}")

    # 4. 데이터 병합 및 저장
    df_result = None
    if df_api is not None and not df_api.empty:
        # 비동기로 DB 저장 (응답 속도 향상)
        # await asyncio.to_thread(db.save_ohlcv, df_api, TARGET_TICKER, interval) 
        # -> sqlite3 스레드 문제 예방을 위해 동기 호출 유지 혹은 별도 처리 필요. 
        # 여기서는 안정성을 위해 동기로 처리하되 로깅 최소화
        db.save_ohlcv(df_api, TARGET_TICKER, interval)
        
        if df_db is not None and not df_db.empty:
            df_result = pd.concat([df_db, df_api])
            df_result = df_result[~df_result.index.duplicated(keep='last')] # 중복 제거
            df_result = df_result.sort_index().iloc[-fetch_count:]
        else:
            df_result = df_api
    elif df_db is not None and not df_db.empty:
        df_result = df_db
        
    return df_result

@app.get("/api/ohlcv")
async def get_ohlcv(interval: str = "minute1", to: str = None, count: int = 200):
    """차트용 OHLCV 및 보조지표 데이터 제공"""
    try:
        loop = asyncio.get_event_loop()
        fetch_count = count + 100 # 지표 계산용 여유분
        
        # 별도 비동기 함수로 분리된 로직 실행
        df = await fetch_ohlcv_data(interval, fetch_count)
        
        if df is None or df.empty:
            return []
            
        # 결측치가 있는 기본 데이터 제거
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        if df.empty:
            return []
            
        # indicators 모듈을 사용하여 지표 추가
        ind.add_all_indicators(df)
        
        # 요청된 개수만큼 자르기
        df = df.iloc[-count:]
        
        # NaN -> None 변환 (JSON 직렬화 호환성)
        df_dict = df.reset_index().to_dict(orient='records')
        
        result = []
        for row in df_dict:
            # 타임스탬프 처리 (컬럼명 'index' 또는 'time')
            ts = row.get('index', row.get('time'))
            if isinstance(ts, (pd.Timestamp, datetime.datetime)):
                ts = int(ts.timestamp())
            
            result.append({
                "time": ts,
                "open": row['open'], "high": row['high'], "low": row['low'], "close": row['close'], "volume": row['volume'],
                "ma1": row.get('ma5'), "ma2": row.get('ma20'), # 호환성 유지
                "bb_upper": row.get('bb_upper'), "bb_lower": row.get('bb_lower'),
                "rsi": row.get('rsi'),
                "macd": row.get('macd'), "macd_signal": row.get('macd_signal'), "macd_hist": row.get('macd_hist')
            })
            
        # None 값을 처리하여 정리
        final_result = []
        for item in result:
            clean_item = {k: (v if pd.notnull(v) else None) for k, v in item.items()}
            final_result.append(clean_item)
            
        return final_result

    except Exception as e:
        print(f"OHLCV API 오류: {e}")
        traceback.print_exc()
        return []

@app.post("/api/start")
async def start_trading(request: dict = None):
    if not state["is_running"]:
        strategy = request.get("strategy", "변동성 돌파") if request else "변동성 돌파"
        
        state["current_strategy"] = strategy
        state["is_running"] = True
        msg = f"🚀 비트코인 자동매매를 시작합니다. (전략: {strategy})"
        add_log(msg)
        send_telegram_message(msg)
        
        thread = threading.Thread(target=trading_logic)
        thread.daemon = True
        thread.start()
    return {"status": "started", "strategy": state["current_strategy"]}

@app.post("/api/stop")
async def stop_trading():
    if state["is_running"]:
        state["is_running"] = False
        msg = "🛑 자동매매를 중지합니다."
        add_log(msg)
        send_telegram_message(msg)
    return {"status": "stopped"}

class BacktestRequest(BaseModel):
    strategy: str = "변동성 돌파"
    period: int = 30
    k: float = 0.5

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    """백테스팅 실행 (비동기)"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, get_backtest_result, request.strategy, request.period, request.k, TARGET_TICKER)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
