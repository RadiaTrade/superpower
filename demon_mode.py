import os
import time
import random
import math
from binance.client import Client
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from scipy.stats import linregress

# Binance API Keys (testnet)
API_KEY = "FEf8x3XU32Hd3a923iT3erconZrmhW77dfXKdpfjMAjpBmW8Ckmv6Fz3RSnVe2Yr"
SECRET_KEY = "LJyOthF5Ohvq24QcVpujHGymjjpRttyn4b6C65qiDOSVNBJNsawAAfdqClQ3un1N"

# Initialize Binance client
client = Client(API_KEY, SECRET_KEY, testnet=True)

# Momentum calculation using Binance kline data
def calculate_momentum(symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=100):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        closes = [float(k[4]) for k in klines]  # Closing prices
        if len(closes) < 2:
            print(f"⚠️ Insufficient data for {symbol}")
            return 0
        slope, _ = linregress(range(len(closes)), closes)[:2]
        return slope / closes[-1]  # Normalized momentum
    except Exception as e:
        print(f"⚠️ Momentum error for {symbol}: {e}")
        return 0

# Get symbol info for trading filters
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

# Adjust quantity to comply with filters
def adjust_quantity(symbol, qty, price):
    filters = get_symbol_filters(symbol)
    if not filters:
        return None
    step_size = filters['step_size']
    min_qty = filters['min_qty']
    min_notional = filters['min_notional']
    
    # Round to step size
    precision = int(round(-math.log10(step_size)))
    qty = round(qty - (qty % step_size), precision)
    
    # Ensure minimums are met
    if qty < min_qty:
        qty = min_qty
    if qty * price < min_notional:
        qty = min_notional / price
        qty = round(qty - (qty % step_size), precision)
    
    return qty

# Place a market order
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

# Get account balances
def get_balances():
    try:
        account = client.get_account()
        balances = {b['asset']: float(b['free']) for b in account['balances'] if float(b['free']) > 0}
        return balances
    except Exception as e:
        print(f"❌ Error fetching balances: {e}")
        return {}

# Main trading loop
def demon_mode_trade():
    print("🔥 Demon Mode activated on Binance Testnet!")
    symbols = ["ETHBTC", "BTCUSDT", "BNBUSDT"]  # Trading pairs
    
    while True:
        # Display balances
        balances = get_balances()
        print(f"💰 Balances: {', '.join(f'{k}={v:.6f}' for k, v in balances.items())}")
        
        for symbol in symbols:
            # Get current price
            try:
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
            except Exception as e:
                print(f"❌ Error fetching price for {symbol}: {e}")
                continue
            
            # Calculate momentum score
            score = calculate_momentum(symbol)
            print(f"📈 {symbol}: Score={score:.3f}, Price={price}")
            
            # Trading logic
            base_asset = symbol[:-4] if symbol.endswith("USDT") else symbol[:-3]
            quote_asset = "USDT" if symbol.endswith("USDT") else "BTC"
            
            if score > 0.3:  # Buy threshold
                qty = 0.001 * balances.get(quote_asset, 0) / price  # 0.1% of quote balance
                qty = adjust_quantity(symbol, qty, price)
                if qty and balances.get(quote_asset, 0) >= qty * price:
                    place_order(symbol, SIDE_BUY, qty)
            elif score < -0.3:  # Sell threshold
                qty = 0.8 * balances.get(base_asset, 0)  # 80% of base balance
                qty = adjust_quantity(symbol, qty, price)
                if qty and balances.get(base_asset, 0) >= qty:
                    place_order(symbol, SIDE_SELL, qty)
        
        # Random delay
        time.sleep(random.randint(10, 20))

if __name__ == "__main__":
    demon_mode_trade()
