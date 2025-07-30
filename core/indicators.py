import pandas as pd
import pandas_ta as ta

def calculate_indicators(ohlcv):
    df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','volume'])
    df['rsi'] = ta.rsi(df['close'], length=14)
    df['ema50'] = ta.ema(df['close'], length=50)
    df['ema200'] = ta.ema(df['close'], length=200)
    macd = ta.macd(df['close'])
    df['macd'] = macd['MACD_12_26_9']
    df['signal'] = macd['MACDs_12_26_9']
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    df['volume'] = df['volume']
    return df.iloc[-1]
