from telegram_bot.notifier import send_message
from core.bybit_api import get_candles

alerts = {}

def add_alert(user_id, symbol, target_price):
    if user_id not in alerts:
        alerts[user_id] = []
    alerts[user_id].append({"symbol": symbol, "target": target_price})
    return f"✅ Алерт установлен для {symbol} при {target_price}$"

def check_alerts():
    for user_id, user_alerts in list(alerts.items()):
        for alert in list(user_alerts):
            candles = get_candles(symbol=alert["symbol"], timeframe="15m")
            price = candles[-1][4]  # close
            if price >= alert["target"]:
                send_message(f"🔔 Цена {alert['symbol']} достигла {alert['target']}$!", chat_id=user_id)
                user_alerts.remove(alert)
        if not user_alerts:
            alerts.pop(user_id)
