import os
import time
import random
import math
import numpy as np
import pandas as pd
from binance.client import Client
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from scipy.stats import linregress

API_KEY = "FEf8x3XU32Hd3a923iT3erconZrmhW77dfXKdpfjMAjpBmW8Ckmv6Fz3RSnVe2Yr"
SECRET_KEY = "LJyOthF5Ohvq24QcVpujHGymjjpRttyn4b6C65qiDOSVNBJNsawAAfdqClQ3un1N"
client = Client(API_KEY, SECRET_KEY, testnet=True)

symbols = ["ETHBTC", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT"]

class TradeLearner:
    def __init__(self):
        self.success_rate = {sym: 0 for sym in symbols}
        self.trade_count = {sym: 0 for sym in symbols}
        self.base_threshold = 0.00005
        self.last_prices = {}
        self.win_streak = {sym: 0 for sym in symbols}
        self.loss_streak = {sym: 0 for sym in symbols}
        self.last_trade_time = {sym: 0 for sym in symbols}
        self.total_losses = 0
        self.loss_window = []
        self.sentiment_history = {sym: [] for sym in symbols}
        self.macd_history = {sym: [] for sym in symbols}

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

def calculate_ema(data, period):
    return pd.Series(data).ewm(span=period, adjust=False).mean().to_numpy()  # Convert back to NumPy

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
        if len(closes) < period + 1:
            raise ValueError(f"Not enough data for RSI ({len(closes)} < {period+1})")
        deltas = np.diff(closes)
        gains = np.maximum(deltas, 0)
        losses = np.abs(np.minimum(deltas, 0))
        avg_gain = calculate_ema(gains, period)[-1]
        avg_loss = calculate_ema(losses, period)[-1]
        rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
        rsi = 100 - (100 / (1 + rs)) if rs != float('inf') else 100
        sentiment = get_x_sentiment(symbol)
        rsi_adj = rsi * (1 + sentiment * 0.5) if abs(sentiment) > 0.5 else rsi
        print(f"📊 RSI for {symbol}: {rsi_adj:.2f} (base {rsi:.2f})")
        return rsi_adj
    except Exception as e:
        print(f"❌ RSI error for {symbol}: {str(e)}")
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

def calculate_macd(symbol, fast_period=12, slow_period=26, signal_period=9):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=slow_period + signal_period)
        closes = np.array([float(k[4]) for k in klines])
        if len(closes) < slow_period + signal_period:
            raise ValueError(f"Not enough data for MACD ({len(closes)} < {slow_period + signal_period})")
        ema_fast = calculate_ema(closes, fast_period)[-1]
        ema_slow = calculate_ema(closes, slow_period)[-1]
        macd_line = ema_fast - ema_slow
        macd_values = [calculate_ema(closes[:i+fast_period], fast_period)[-1] - 
                       calculate_ema(closes[:i+slow_period], slow_period)[-1] 
                       for i in range(len(closes)-slow_period-signal_period+1, len(closes))]
        signal_line = calculate_ema(macd_values, signal_period)[-1]
        learner.macd_history[symbol].append((macd_line, signal_line))
        if len(learner.macd_history[symbol]) > 2:
            learner.macd_history[symbol].pop(0)
        print(f"📊 MACD for {symbol}: MACD={macd_line:.4f}, Signal={signal_line:.4f}")
        return macd_line, signal_line
    except Exception as e:
        print(f"❌ MACD error for {symbol}: {str(e)}")
        return 0, 0

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
    qty = max(min_qty, qty)
    if qty * price < min_notional:
        qty = min_notional / price
    qty = round(qty - (qty % step_size), precision)
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
    scores_history = {symbol: [] for symbol in symbols}
    
    while True:
        try:
            balances = get_balances()
            if not balances:
                print("⚠️ Failed to fetch balances, retrying in 10 seconds...")
                time.sleep(10)
                continue
            print(f"💰 Balances: {', '.join(f'{k}={v:.6f}' for k, v in balances.items())}")
            print(f"💸 Total P/L: {tracker.get_pl():.2f} USDT")
        except Exception as e:
            print(f"❌ Error in demon_mode_trade: {e}")
            time.sleep(10)
            continue
        
        if len(learner.loss_window) >= 5:
            print("⚠️ Failsafe triggered—5 losses in 1 hour, pausing for 5 mins!")
            time.sleep(300)
            learner.loss_window = []
            continue
        
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
            macd, signal = calculate_macd(symbol)
            breakout = detect_breakout(symbol)
            volume_spike = detect_volume_spike(symbol)
            
            value_factor = 1 if ma50 and price < ma50 else -1 if ma50 and price > ma50 else 0
            pump_risk = 1 if volume_spike and rsi > 80 and momentum < 0 else 0
            z_score = (momentum - np.mean(scores_history[symbol][-20:])) / np.std(scores_history[symbol][-20:]) if scores_history[symbol] and np.std(scores_history[symbol][-20:]) > 0 else 0
            
            macd_cross = 0
            if len(learner.macd_history[symbol]) >= 2:
                prev_macd, prev_signal = learner.macd_history[symbol][-2]
                macd_cross = 1 if prev_macd < prev_signal and macd > signal else -1 if prev_macd > prev_signal and macd < signal else 0
            
            dom_score = (
                0.3 * momentum +
                0.2 * (rsi - 50) / 50 +
                0.2 * sentiment +
                0.2 * breakout +
                0.1 * value_factor +
                0.1 * macd_cross
            ) * (1 if abs(z_score) > 1 else 0.5)
            
            if pump_risk:
                dom_score -= 1
            
            scores_history[symbol].append(dom_score)
            print(f"💥 {symbol}: Dom Score={dom_score:.3f}, Price={price}")
            
            buy_threshold = learner.update(symbol, SIDE_BUY, 0, price)
            sell_threshold = -buy_threshold
            base_asset = symbol[:-4] if symbol.endswith("USDT") else symbol[:-3]
            quote_asset = "USDT" if symbol.endswith("USDT") else "BTC"
            atr_factor = max(1, atr / price)
            leverage = min(2.5, 1 + (learner.win_streak[symbol] * 0.1)) if learner.win_streak[symbol] >= 5 else max(0.5, 1 - (learner.loss_streak[symbol] * 0.1)) if learner.loss_streak[symbol] >= 3 else 1
            ma_slope = (ma50 - np.mean([float(k[4]) for k in client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=51)[:-1]])) / 50 if ma50 else 0
            leverage_cap = 2.5 if ma_slope > 0 else 1.5
            leverage = min(leverage_cap, leverage)
            size_factor = 2 if sentiment > 0.9 else 0.25 if sentiment < -0.9 else 1
            trade_freq = min(1, atr / price)
            
            if dom_score > buy_threshold and rsi < 70 and not pump_risk and (sentiment > 0.5 or sentiment < -0.5 or macd_cross > 0) and random.random() < trade_freq:
                qty = (0.05 * balances.get(quote_asset, 0) / price) * (1 / atr_factor) * leverage * size_factor
                qty = adjust_quantity(symbol, qty, price)
                quote_price = price if quote_asset == "USDT" else price * float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
                if qty and balances.get(quote_asset, 0) >= qty * price and qty * quote_price >= 10:
                    order, exec_price = place_order(symbol, SIDE_BUY, qty)
                    if order:
                        learner.update(symbol, SIDE_BUY, qty, exec_price)
                        tracker.update(symbol, SIDE_BUY, qty, exec_price)
            elif (dom_score < sell_threshold or rsi > 70 or macd_cross < 0) and balances.get(base_asset, 0) > 0.001 and random.random() < trade_freq:
                qty = balances.get(base_asset, 0)  # Sell full position
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