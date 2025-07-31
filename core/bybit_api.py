import ccxt
from config import BYBIT_API_KEY, BYBIT_API_SECRET

exchange = ccxt.bybit({
    "apiKey": BYBIT_API_KEY,
    "secret": BYBIT_API_SECRET,
    "enableRateLimit": True,
})

def get_candles(symbol="BTC/USDT", timeframe="15m", limit=200):
    markets = exchange.load_markets()
    if symbol not in markets:
        alt_symbol = symbol.replace("/", "")
        if alt_symbol in markets:
            symbol = alt_symbol
        else:
            raise ValueError(f"❌ Пара {symbol} не найдена на Bybit.")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    return ohlcv
