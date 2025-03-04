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

def check_news(symbol):
    if symbol == "BTCUSDT" and random.random() < 0.1:
        print(f"🚨 News Alert: Binance hack rumor for {symbol}")
        return "crash"
    return "normal"

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

def detect_anomaly(scores, window=20):
    if len(scores) < window:
        return 0.002, -0.001  # Buy threshold raised to 0.002
    mean, std = np.mean(scores[-window:]), np.std(scores[-window:])
    z = (scores[-1] - mean) / std if std > 0 else 0
    return (0.005, -0.005) if abs(z) > 2 else (0.002, -0.001)

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

def place_order(symbol, side, qty):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=qty
        )
        print(f"✅ {side} {qty} {symbol} @ market price")
        return order
    except Exception as e:
        print(f"❌ Error placing {side} order for {symbol}: {e}")
        return None

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
    symbols = ["ETHBTC", "BTCUSDT", "BNBUSDT"]
    scores_history = {symbol: [] for symbol in symbols}
    
    while True:
        balances = get_balances()
        print(f"💰 Balances: {', '.join(f'{k}={v:.6f}' for k, v in balances.items())}")
        
        for symbol in symbols:
            try:
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
            except Exception as e:
                print(f"❌ Error fetching price for {symbol}: {e}")
                continue
            
            score = calculate_momentum(symbol)
            scores_history[symbol].append(score)
            print(f"📈 {symbol}: Score={score:.3f}, Price={price}")
            
            buy_threshold, sell_threshold = detect_anomaly(scores_history[symbol])
            news_event = check_news(symbol)
            base_asset = symbol[:-4] if symbol.endswith("USDT") else symbol[:-3]
            quote_asset = "USDT" if symbol.endswith("USDT") else "BTC"
            
            if news_event == "crash":
                qty = 0.8 * balances.get(base_asset, 0)
                qty = adjust_quantity(symbol, qty, price)
                if qty and balances.get(base_asset, 0) >= qty:
                    place_order(symbol, SIDE_SELL, qty)
            elif score > buy_threshold:
                qty = 0.02 * balances.get(quote_asset, 0) / price
                qty = adjust_quantity(symbol, qty, price)
                if qty and balances.get(quote_asset, 0) >= qty * price:
                    place_order(symbol, SIDE_BUY, qty)
            elif score < sell_threshold:
                qty = 0.8 * balances.get(base_asset, 0)
                qty = adjust_quantity(symbol, qty, price)
                if qty and balances.get(base_asset, 0) >= qty:
                    place_order(symbol, SIDE_SELL, qty)
        
        time.sleep(random.randint(10, 20))

if __name__ == "__main__":
    demon_mode_trade()