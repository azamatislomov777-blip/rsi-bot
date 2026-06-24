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
    "AVAXUSDT"
]

sent_signals = set()


def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )

    except Exception as e:
        print("Telegram Error:", e)


def get_klines(symbol, interval="4h", limit=200):

    try:

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        data = response.json()

        if not isinstance(data, list):
            print(f"Binance Error {symbol}: {data}")
            return None

        closes = []

        for candle in data:

            if len(candle) < 5:
                return None

            closes.append(float(candle[4]))

        return pd.DataFrame({
            "close": closes
        })

    except Exception as e:

        print(f"{symbol} error:", e)

        return None


def check_signal(symbol, timeframe):

    df = get_klines(symbol, timeframe)

    if df is None:
        return

    if len(df) < 50:
        return

    try:

        rsi = RSIIndicator(
            close=df["close"],
            window=14
        ).rsi()

        current_rsi = float(rsi.iloc[-1])
        previous_rsi = float(rsi.iloc[-2])

        price = float(df["close"].iloc[-1])

        signal = None

        if previous_rsi < 30 and current_rsi > 30:
            signal = "BUY"

        elif previous_rsi > 70 and current_rsi < 70:
            signal = "SELL"

        if signal:

            signal_key = f"{symbol}_{timeframe}_{signal}"

            if signal_key in sent_signals:
                return

            sent_signals.add(signal_key)

            emoji = "🟢" if signal == "BUY" else "🔴"

            message = f"""
{emoji} {signal} SIGNAL

Coin: {symbol}
Timeframe: {timeframe.upper()}

Price: {price:.4f}

RSI: {previous_rsi:.2f} → {current_rsi:.2f}

Timeframe Status: CONFIRMED

Time: UTC
"""

            send_message(message)

            print(message)

    except Exception as e:

        print("RSI Error:", e)


def run_bot():

    send_message("🚀 RSI Bot v1.0 started")

    while True:

        try:

            for coin in COINS:

                check_signal(coin, "4h")
                check_signal(coin, "1d")

            print("✅ Check completed")

        except Exception as e:

            print("MAIN ERROR:", e)

        time.sleep(1200)


if __name__ == "__main__":
    run_bot()
