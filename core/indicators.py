import pandas as pd
import pandas_ta as ta

def calculate_indicators(candles):
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    df["ema50"] = ta.ema(df["close"], length=50)
    df["ema200"] = ta.ema(df["close"], length=200)
    df["rsi"] = ta.rsi(df["close"], length=14)

    macd = ta.macd(df["close"])
    df["macd"] = macd["MACD_12_26_9"]
    df["signal"] = macd["MACDs_12_26_9"]

    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["volume_mean"] = df["volume"].rolling(window=20).mean()

    data = {
        "close": df["close"].iloc[-1],
        "ema50": df["ema50"].iloc[-1],
        "ema200": df["ema200"].iloc[-1],
        "rsi": df["rsi"].iloc[-1],
        "macd": df["macd"].iloc[-1],
        "signal": df["signal"].iloc[-1],
        "atr": df["atr"].iloc[-1],
        "volume": df["volume"].iloc[-1],
        "volume_mean": df["volume_mean"].iloc[-1],
        "prices": df["close"].tolist(),
        "df": df
    }

    # добавляем флаг для проверки пересечения EMA50 и EMA200
    data["prev_ema_cross"] = df["ema50"].iloc[-2] > df["ema200"].iloc[-2]

    return data
