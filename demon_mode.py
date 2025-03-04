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
                old_price = self.positions[symbol]['avg_price']
                new_qty = old_qty + qty
                new_avg_price = (old_price * old_qty + usd_price * qty) / new_qty
                self.positions[symbol] = {'qty': new_qty, 'avg_price': new_avg_price}
            else:
                self.positions[symbol] = {'qty': qty, 'avg_price': usd_price}
        elif side == SIDE_SELL and symbol in self.positions:
            if self.positions[symbol]['qty'] >= qty:
                buy_price = self.positions[symbol]['avg_price']
                profit = (usd_price - buy_price) * qty
                self.total_pl += profit
                self.positions[symbol]['qty'] -= qty
                if self.positions[symbol]['qty'] <= 0:
                    del self.positions[symbol]

    def get_pl(self):
        return self.total_pl

learner = TradeLearner()
tracker = TradeTracker()

def get_x_sentiment(symbol):
    posts = [f"{symbol.split('USDT')[0] if 'USDT' in symbol else symbol} to the moon!", f"Dumping {symbol} hard rn", f"{symbol} steady as hell"]
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

def calculate_atr(symbol, period=14):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=period+1)
        highs = np.array([float(k[2]) for k in klines])
        lows = np.array([float(k[3]) for k in klines])
        closes = np.array([float(k[4]) for k in klines])
        tr = np.maximum(highs[1:], closes[:-1]) - np.minimum(lows[1:], closes[:-1])
        atr = np.mean(tr)
        print(f"📈 ATR for {symbol}: {atr:.4f}")
        return atr
    except Exception as e:
        print(f"❌ ATR error for {symbol}: {e}")
        return 1

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
    qty = max(min_qty, qty)  # Ensure at least min_qty
    if qty * price < min_notional:
        qty = min_notional / price
    qty = round(qty - (qty % step_size), precision)  # Clean step
    return qty

def get_symbol_filters(symbol):
    try:
        info = client.get_symbol_info(symbol)
        filters = {f['filterType']: f for f in info['filters']}
        return {
            'min_qty': float(filters['LOT_SIZE']['minQty']),
            'step_size': float(filters['LOT_SIZE']['stepSize']),
            'min_notional': float(filters['NOTIONAL']['minNotional'])
        }
    except Exception as e:
        print(f"❌ Error fetching filters for {symbol}: {e}")
        return None

def place_order(symbol, side, qty):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=qty
        )
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        print(f"✅ {side} {qty} {symbol} @ market price (~{price})")
        return order, price
    except Exception as e:
        print(f"❌ Error placing {side} order for {symbol}: {e}")
        return None, None

def get_balances():
    try:
        account = client.get_account()
        balances = {b['asset']: float(b['free']) for b in account['balances'] if float(b['free']) > 0}
        return balances
    except Exception as e:
        print(f"❌ Error fetching balances: {e}")
        return {}

def demon_mode_trade():
    print("🔥 Demon Mode activated on Binance Testnet!")
    symbols = ["ETHBTC", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT"]
    scores_history = {symbol: [] for symbol in symbols}
    
    while True:
        balances = get_balances()
        print(f"💰 Balances: {', '.join(f'{k}={v:.6f}' for k, v in balances.items())}")
        print(f"💸 Total P/L: {tracker.get_pl():.2f} USDT")
        
        for symbol in symbols:
            try:
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
            except Exception as e:
                print(f"❌ Error fetching price for {symbol}: {e}")
                continue
            
            momentum = calculate_momentum(symbol)
            rsi = calculate_rsi(symbol)
            sentiment = get_x_sentiment(symbol)
            ma50 = calculate_moving_average(symbol)
            atr = calculate_atr(symbol)
            breakout = detect_breakout(symbol)
            volume_spike = detect_volume_spike(symbol)
            
            value_factor = 1 if ma50 and price < ma50 else -1 if ma50 and price > ma50 else 0
            pump_risk = 1 if volume_spike and rsi > 80 and momentum < 0 else 0
            z_score = (momentum - np.mean(scores_history[symbol][-20:])) / np.std(scores_history[symbol][-20:]) if scores_history[symbol] and np.std(scores_history[symbol][-20:]) > 0 else 0
            
            dom_score = (
                0.3 * momentum +
                0.2 * (rsi - 50) / 50 +
                0.2 * sentiment +
                0.2 * breakout +
                0.1 * value_factor
            ) * (1 if abs(z_score) > 1 else 0.5)
            
            if pump_risk:
                dom_score -= 1
            
            scores_history[symbol].append(dom_score)
            print(f"💥 {symbol}: Dom Score={dom_score:.3f}, Price={price}")
            
            buy_threshold = learner.update(symbol, SIDE_BUY, 0, price)
            sell_threshold = -buy_threshold
            base_asset = symbol[:-4] if symbol.endswith("USDT") else symbol[:-3]
            quote_asset = "USDT" if symbol.endswith("USDT") else "BTC"
            atr_factor = max(1, atr / price)  # Normalize ATR
            
            if dom_score > buy_threshold and rsi < 70 and not pump_risk:
                qty = (0.05 * balances.get(quote_asset, 0) / price) * (1 / atr_factor)
                qty = adjust_quantity(symbol, qty, price)
                quote_price = price if quote_asset == "USDT" else price * float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
                if qty and balances.get(quote_asset, 0) >= qty * price and qty * quote_price >= 10:
                    order, exec_price = place_order(symbol, SIDE_BUY, qty)
                    if order:
                        learner.update(symbol, SIDE_BUY, qty, exec_price)
                        tracker.update(symbol, SIDE_BUY, qty, exec_price)
            elif (dom_score < sell_threshold or rsi > 70) and balances.get(base_asset, 0) > 0.001:
                qty = min(0.8 * balances.get(base_asset, 0), balances.get(base_asset, 0)) * (1 / atr_factor)
                qty = adjust_quantity(symbol, qty, price)
                quote_price = price if quote_asset == "USDT" else price * float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
                if qty and balances.get(base_asset, 0) >= qty and qty * quote_price >= 10:
                    order, exec_price = place_order(symbol, SIDE_SELL, qty)
                    if order:
                        learner.update(symbol, SIDE_SELL, qty, exec_price)
                        tracker.update(symbol, SIDE_SELL, qty, exec_price)
        
        time.sleep(random.randint(5, 10))

if __name__ == "__main__":
    demon_mode_trade()