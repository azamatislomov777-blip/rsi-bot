import os
import time
import requests
import pandas as pd
from ta.momentum import RSIIndicator

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

COINS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "TONUSDT"
]

sent_signals = {}

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

def get_klines(symbol, interval="4h", limit=200):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    data = requests.get(url, params=params).json()

    closes = [float(x[4]) for x in data]

    return pd.DataFrame({
        "close": closes
    })

def check_rsi_signal(symbol, timeframe):

    df = get_klines(symbol, timeframe)

    rsi = RSIIndicator(df["close"], window=14).rsi()

    current_rsi = float(rsi.iloc[-1])
    previous_rsi = float(rsi.iloc[-2])

    price = float(df["close"].iloc[-1])

    signal = None

    # BUY
    if previous_rsi < 30 and current_rsi > 30:
        signal = "BUY"

    # SELL
    elif previous_rsi > 70 and current_rsi < 70:
        signal = "SELL"

    if signal:

        signal_key = f"{symbol}_{timeframe}_{signal}"

        if signal_key in sent_signals:
            return

        sent_signals[signal_key] = True

        emoji = "🟢" if signal == "BUY" else "🔴"

        message = f"""
{emoji} {signal} SIGNAL

Coin: {symbol}
Timeframe: {timeframe.upper()}

Price: {price:.4f}

RSI: {previous_rsi:.2f} → {current_rsi:.2f}

Time: UTC
"""

        send_message(message)

        print(message)

def run_bot():

    send_message("🚀 RSI Bot v1.0 started")

    while True:

        try:

            for coin in COINS:

                check_rsi_signal(coin, "4h")
                check_rsi_signal(coin, "1d")

            print("Check completed")

        except Exception as e:

            print("ERROR:", e)

        time.sleep(1200)

if __name__ == "__main__":
    run_bot()
