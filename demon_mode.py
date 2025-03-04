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
        self.success_rate = {sym: 0 for sym in ["ETHBTC", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT"]}
        self.trade_count = {sym: 0 for sym in ["ETHBTC", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT"]}
        self.base_threshold = 0.00005
        self.last_prices = {}
        self.win_streak = {sym: 0 for sym in ["ETHBTC", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT"]}
        self.loss_streak = {sym: 0 for sym in ["ETHBTC", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT"]}
        self.last_trade_time = {sym: 0 for sym in ["ETHBTC", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT"]}
        self.total_losses = 0
        self.loss_window = []
        self.sentiment_history = {sym: [] for sym in ["ETHBTC", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT"]}
        self.macd_history = {sym: [] for sym in symbols}  # Store MACD history

    def update(self, symbol, side, qty, price):
        current_time = time.time()
        if side == SIDE_SELL and symbol in self.last_prices:
            profit = (price - self.last_prices[symbol]) * qty
            self.trade_count[symbol] += 1
            self.success_rate[symbol] = (self.success_rate[symbol] * (self.trade_count[symbol] - 1) + (1 if profit > 0 else 0)) / self.trade_count[symbol]
            if profit > 0:
                self.win_streak[symbol] += 1
                self.loss_streak[symbol] = 0
            else:
                self.loss_streak[symbol] += 1
                self.win_streak[symbol] = 0
                self.total_losses += 1
                self.loss_window.append(current_time)
            self.loss_window = [t for t in self.loss_window if current_time - t < 3600]
        if side == SIDE_BUY:
            self.last_prices[symbol] = price
        self.last_trade_time[symbol] = current_time
        return self.base_threshold * (1 + self.success_rate[symbol] - 0.5)

class TradeTracker:
    def __init__(self):
        self.total_pl = 0
        self.positions = {}

    def update(self, symbol, side, qty, price):
        quote = "USDT" if symbol.endswith("USDT") else "BTC"
        usd_price = price if quote == "USDT" else price * float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
        
        if side == SIDE_BUY:
            if symbol in self.positions:
                old_qty = self.positions[symbol]['qty']
                old_cost = self.positions[symbol]['cost_basis_usdt']
                new_qty = old_qty + qty
                new_cost = old_cost + (qty * usd_price)
                self.positions[symbol] = {'qty': new_qty, 'cost_basis_usdt': new_cost}
            else:
                self.positions[symbol] = {'qty': qty, 'cost_basis_usdt': qty * usd_price}
            print(f"📈 Buy {qty} {symbol} @ {usd_price:.2f} USD - Cost basis: {self.positions[symbol]['cost_basis_usdt']:.2f} USDT")
        
        elif side == SIDE_SELL and symbol in self.positions:
            if self.positions[symbol]['qty'] >= qty:
                old_qty = self.positions[symbol]['qty']
                old_cost = self.positions[symbol]['cost_basis_usdt']
                avg_buy_price = old_cost / old_qty
                profit = (usd_price - avg_buy_price) * qty
                self.total_pl += profit
                new_qty = old_qty - qty
                new_cost = old_cost - (avg_buy_price * qty)
                if new_qty > 0:
                    self.positions[symbol] = {'qty': new_qty, 'cost_basis_usdt': new_cost}
                else:
                    del self.positions[symbol]
                print(f"📉 Sell {qty} {symbol} @ {usd_price:.2f} USD - Profit: {profit:.2f} USDT, Total P/L: {self.total_pl:.2f} USDT")

    def get_pl(self):
        return self.total_pl

learner = TradeLearner()
tracker = TradeTracker()

def get_x_sentiment(symbol):
    posts = [f"{symbol.split('USDT')[0] if 'USDT' in symbol else symbol} to the moon!", f"Dumping {symbol} hard rn", f"{symbol} steady as hell"]
    sentiment_score = sum(1 if "moon" in p.lower() else -1 if "dump" in p.lower() else 0 for p in posts)
    sentiment = sentiment_score / max(len(posts), 1)
    learner.sentiment_history[symbol].append(sentiment)
    if len(learner.sentiment_history[symbol]) > 5:
        learner.sentiment_history[symbol].pop(0)
    smoothed_sentiment = np.mean(learner.sentiment_history[symbol]) if learner.sentiment_history[symbol] else sentiment
    print(f"🗣️ X Sentiment for {symbol}: {smoothed_sentiment:.2f} (raw {sentiment:.2f})")
    return smoothed_sentiment

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
        sentiment = get_x_sentiment(symbol)
        rsi_adj = rsi * (1 + sentiment * 0.5) if abs(sentiment) > 0.5 else rsi
        print(f"📊 RSI for {symbol}: {rsi_adj:.2f} (base {rsi:.2f})")
        return rsi_adj
    except Exception as e:
        print(f"❌ RSI error for {symbol}: {e}")
        return 50

def calculate_moving_averag