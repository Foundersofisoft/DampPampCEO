from datetime import datetime
import pytz

TIMEZONE = pytz.timezone("Asia/Almaty")

def find_support_resistance(prices, window=20):
    support = min(prices[-window:])
    resistance = max(prices[-window:])
    return support, resistance

def check_hot_signal(data):
    if data['rsi'] < 25 or data['rsi'] > 75:
        return True
    if (data['ema50'] > data['ema200'] and not data['prev_ema_cross']) or (data['ema50'] < data['ema200'] and data['prev_ema_cross']):
        return True
    return False

def generate_signal(data, symbol="BTC/USDT", timeframe="15m"):
    price = round(data['close'], 3)
    atr = data['atr']
    support, resistance = find_support_resistance(data['prices'])
    hot = check_hot_signal(data)

    if data['rsi'] < 30 and data['ema50'] > data['ema200']:
        trend = "📈 LONG (RSI низкий + EMA бычья)"
    elif data['rsi'] > 70 and data['ema50'] < data['ema200']:
        trend = "📉 SHORT (RSI высокий + EMA медвежья)"
    elif data['ema50'] > data['ema200']:
        trend = "📈 LONG тренд"
    elif data['ema50'] < data['ema200']:
        trend = "📉 SHORT тренд"
    else:
        trend = "⚖️ Боковое движение"

    tp1 = round(price + atr * 1.5, 3)
    tp2 = round(price + atr * 3, 3)
    tp3 = round(resistance, 3)
    sl = round(support, 3)

    local_time = datetime.now(TIMEZONE).strftime("%H:%M %d-%m-%Y")
    emoji = "🔥" if hot else "📊"

    return f"""
━━━━━━━━━━━━━━━━━━━
{emoji} МОНИТА: *{symbol.replace('/', '')}*
⏱ Таймфрейм: {timeframe}
{trend}
🪙 ПЛЕЧО: 10x

💵 Вход: `{price}$`
🎯 TP: `{tp1}$` / `{tp2}$` / `{tp3}$`
🛑 SL: `{sl}$`

📊 RSI: `{round(data['rsi'],2)}` | EMA50: `{round(data['ema50'],3)}` | EMA200: `{round(data['ema200'],3)}`
📊 MACD: `{round(data['macd'],4)}` | Signal: `{round(data['signal'],4)}`
📊 ATR: `{round(atr,3)}` | Volume: `{round(data['volume'],2)}`
🕒 Время анализа: `{local_time}`
━━━━━━━━━━━━━━━━━━━
"""