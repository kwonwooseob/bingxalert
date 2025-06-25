import requests
import hmac
import hashlib
import time
import json
from flask import Flask
from telegram import Bot

# 🔐 대표님의 정보 입력
API_KEY = "fN22ZU3OzewbsDqNy3iNsZmeTkqOsNEjLNhtKgq4UNguVmIBBdA8GkADBVDE2vqMwB907NY4CKtVavSG62kg"
SECRET_KEY = "oFxR37C69dIdDnx7N7F4COPM5rldFs4EcPjFffJRwnTrnNTR3qzV7GFPpodd37aPi9GjzPOrg8HbOspZFNGw"
BOT_TOKEN = "7906284554:AAGKppB89hHzqCVDq0akfRMAjs_mM8FoHBc"
CHAT_ID = "5636838694"

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

def sign(query_string, secret_key):
    return hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_positions():
    timestamp = str(int(time.time() * 1000))
    recvWindow = "5000"
    query_string = f"timestamp={timestamp}&recvWindow={recvWindow}"
    signature = sign(query_string, SECRET_KEY)

    headers = {
        "X-BX-APIKEY": API_KEY
    }

    url = f"https://open-api.bingx.com/openApi/swap/v2/user/positions?{query_string}&signature={signature}"
    response = requests.get(url, headers=headers)
    
    print("🔍 API 응답 확인:", response.text)  # ✅ 이 줄 추가
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

def check_and_notify():
    data = get_positions()
    if "data" in data:
        for position in data["data"]:
            symbol = position.get("symbol")
            side = position.get("positionSide")
            size = position.get("positionAmt")
            entry = position.get("entryPrice")
            msg = f"[{symbol}] {side} 진입!\n수량: {size}, 진입가: {entry}"
            bot.send_message(chat_id=CHAT_ID, text=msg)

@app.route('/')
def index():
    return "Bot is alive"

@app.route('/run')
def run_check():
    print("🚀 /run 실행됨")  # ✅ 이것도 함께 추가
    check_and_notify()
    return "Check done!"

@app.route('/check', methods=['GET'])
def check_positions():
    data = get_positions()

    if "error" in data:
        message = f"[❗에러] {data['error']}"
    else:
        positions = data.get("data", [])
        if not positions:
            message = "[📭] 현재 포지션이 없습니다."
        else:
            message = "[📈 현재 포지션]\n"
            for pos in positions:
                symbol = pos.get("symbol")
                side = pos.get("side")
                pnl = pos.get("realizedPnl")
                message += f"{symbol} - {side} - 수익: {pnl}\n"

    bot.send_message(chat_id=CHAT_ID, text=message)
    return "텔레그램으로 보냈어요!"

# ✅ 여기 위치가 중요합니다
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500)
