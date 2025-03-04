import os
import time
import random
import math
import numpy as np
from binance.client import Client
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from scipy.stats import linregress

API_KEY = "FEf8x3XU32Hd3a923iT3erconZrmhW77dfXKdpfjMAjpBmW8Ckmv6Fz3RSnVe2Yr"
SECRET_KEY = "LJyOthF5Ohvq24QcVpujHGymjjpRttyn4b6C65qiDOSVNBJNsawAAfdqClQ3un1N"
client = Client(API_KEY, SECRET_KEY, testnet=True)

class TradeLearner:
    def __init__(self):
        self.success_rate = 0
        self.trade_count = 0
        self.base_threshold = 0.00005
        self.last_prices = {}

    def update(self, symbol, side, qty, price):
        if side == SIDE_SELL and symbol in self.last_prices:
            profit = (price - self.last_prices[symbol]) * qty
            self.trade_count += 1
            self.success_rate = (self.success_rate * (self.trade_count - 1) + (1 if profit > 0 else 0)) / self.trade_count
        if side == SIDE_BUY:
            self.last_prices[symbol] = price
        return self.base_threshold * (1 + self.success_rate - 0.5)

learner = TradeLearner()

def get_x_sentiment(symbol):
    # Mocked X posts - replace with real fetch later
    posts = [
        f"{symbol.split('USDT')[0] if 'USDT' in symbol else symbol} to the moon!",
        f"Dumping {symbol} hard rn",
        f"{symbol} steady as hell"
    ]
    sentiment_score = sum(1 if "moon" in p.lower() else -1 if "dump" in p.lower() else 0 for p in posts)
    sentiment = sentiment_score / max(len(posts), 1)
    print(f"🗣️ X Sentiment for {symbol}: {sentiment:.2f}")
    return sentiment

def calculate_momentum(symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=100):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        closes = [float(k[4]) for k in klines]
        if len(closes) < 2:
            print(f"⚠️ Insufficient data for {symbol}")
            return 0
        slope, _ = linregress(range(len(closes)), closes)[:2]
        return slope / closes[-1]
    except Exception as e:
        print(f"⚠️ Momentum error for {symbol}: {e}")
        return 0

def calculate_rsi(symbol, period=14):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=period+1)
        closes = np.array([float(k[4]) for k in klines])
        deltas = np.diff(closes)
        gain = np.mean(deltas * (deltas > 0))
        loss = -np.mean(deltas * (deltas < 0))
        rs = gain / loss if loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        print(f"📊 RSI for {symbol}: {rsi:.2f}")
        return rsi
    except Exception as e:
        print(f"❌ RSI error for {symbol}: {e}")
        return 50

def calculate_moving_average(symbol, period=50):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=period)
        closes = [float(k[4]) for k in klines]
        ma = np.mean(closes)
        print(f"📉 MA50 for {symbol}: {ma:.2f}")
        return ma
    except Exception as e:
        print(f"❌ MA error for {symbol}: {e}")
        return None

def detect_breakout(symbol, limit=100):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=limit)
        highs = [float(k[2]) for k in klines]
        resistance = max(highs[:-1])
        current = float(klines[-1][4])
        if current > resistance:
            print(f"🚀 Breakout detected for {symbol}: {current} > {resistance}")
            return 1
        return 0
    except Exception as e:
        print(f"❌ Breakout error for {symbol}: {e}")
        return 0

def detect_volume_spike(symbol, limit=20):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=limit)
        volumes = [float(k[5]) for k in klines]
        avg_vol = np.mean(volumes[:-1])
        current_vol = volumes[-1]
        if current_vol > 2 * avg_vol:
            print(f"📢 Volume spike for {symbol}: {current_vol:.2f} vs avg {avg_vol:.2f}")
            return 1
        return 0
    except Exception as e:
        print(f"❌ Volume error for {symbol}: {e}")
        return 0

def adjust_quantity(symbol, qty, price):
    filters = get_symbol_filters(symbol)
    if not filters:
        return None
    step_size = filters['step_size']
    min_qty = filters['min_qty']
    min_notional = filters['min_notional']
    precision = int(round(-math.log10(step_size)))
    qty = round(qty - (qty % step_size), precision)
    if qty < min_qty:
        qty = min_qty
    if qty * price < min_notional:
        qty = min_notional / price
        qty = round(qty - (qty % step_size), precision)
    return qty

def get_symbol_filters(symbol):
    try:
        info = client.get_symbol_info(symbol)
        filters 