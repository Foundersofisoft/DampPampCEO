from datetime import datetime
import pytz
import pandas_ta as ta

TIMEZONE = pytz.timezone("Asia/Almaty")

def generate_signal(data, symbol="ATOM/USDT", timeframe="15m"):
    price = round(data['close'], 2)
    macd_cross = data['macd'] > data['signal']
    atr = data['atr']
    volume = data['volume']

    # логика анализа
    if data['rsi'] < 30 and data['ema50'] > data['ema200'] and macd_cross:
        trend = "📈 *LONG* (RSI низкий + MACD вверх)"
    elif data['rsi'] > 70 and data['ema50'] < data['ema200'] and not macd_cross:
        trend = "📉 *SHORT* (RSI высокий + MACD вниз)"
    elif data['ema50'] > data['ema200']:
        trend = "📈 *LONG тренд* (EMA50 > EMA200)"
    elif data['ema50'] < data['ema200']:
        trend = "📉 *SHORT тренд* (EMA50 < EMA200)"
    else:
        trend = "⚖️ *Боковое движение*"

    # динамические TP и SL через ATR
    tp1 = round(price + atr * 1.5, 2)
    tp2 = round(price + atr * 3, 2)
    tp3 = round(price + atr * 4.5, 2)
    sl = round(price - atr * 2, 2)

    local_time = datetime.now(TIMEZONE).strftime("%H:%M %d-%m-%Y")

    return f"""
━━━━━━━━━━━━━━━━━━━
💎 МОНИТА: *{symbol.replace('/', '')}*
⏱ Таймфрейм: {timeframe}
{trend}
🪙 ПЛЕЧО: 10x

💵 Вход: `{price}$`
🎯 TP: `{tp1}$` / `{tp2}$` / `{tp3}$`
🛑 SL: `{sl}$`

📊 RSI: `{round(data['rsi'],2)}` | EMA50: `{round(data['ema50'],3)}` | EMA200: `{round(data['ema200'],3)}`
📊 MACD: `{round(data['macd'],4)}` | Signal: `{round(data['signal'],4)}`
📊 ATR: `{round(atr,3)}` | Объём: `{round(volume,2)}`
🕒 Время анализа: `{local_time}`
━━━━━━━━━━━━━━━━━━━
"""
