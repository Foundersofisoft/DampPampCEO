from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from core.bybit_api import get_candles
from core.indicators import calculate_indicators
from core.strategy import generate_signal
from telegram_bot.notifier import send_message
from config import TELEGRAM_TOKEN
import pytz
from datetime import datetime

TIMEZONE = pytz.timezone("Asia/Almaty")

# список монет
COINS = {
    "BTC/USDT": "₿ BTC",
    "ETH/USDT": "Ξ ETH",
    "ATOM/USDT": "⚛ ATOM",
    "BNB/USDT": "🟡 BNB",
    "SOL/USDT": "🌞 SOL",
    "XRP/USDT": "💠 XRP",
    "ADA/USDT": "🔷 ADA",
    "DOGE/USDT": "🐶 DOGE",
    "DOT/USDT": "🎯 DOT",
    "MATIC/USDT": "🔺 MATIC",
    "ARB/USDT": "🌀 ARB",   # 👈 Добавили Arbitrum
}

# таймфреймы
TIMEFRAMES = {
    "5m": "⏱ 5m",
    "15m": "⏱ 15m",
    "1h": "🕒 1h",
    "4h": "🕓 4h",
}

# главное меню монет
def get_main_menu():
    keyboard = [[InlineKeyboardButton(f"{emoji}", callback_data=f"coin|{symbol}")] for symbol, emoji in COINS.items()]
    return InlineKeyboardMarkup(keyboard)

# меню таймфреймов
def get_tf_menu(symbol):
    keyboard = [[InlineKeyboardButton(f"{emoji}", callback_data=f"tf|{symbol}|{tf}")]
                for tf, emoji in TIMEFRAMES.items()]
    keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

# команда /signals
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Выбери монету для анализа:", reply_markup=get_main_menu())

# обработка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")

    # назад к списку монет
    if query.data == "back":
        await query.edit_message_text("📊 Выбери монету для анализа:", reply_markup=get_main_menu())
        return

    # выбор монеты
    if data[0] == "coin":
        symbol = data[1]
        await query.edit_message_text(f"⏱ Выбери таймфрейм для {symbol}:", reply_markup=get_tf_menu(symbol))
        return

    # выбор таймфрейма
    if data[0] == "tf":
        symbol = data[1]
        tf = data[2]
        candles = get_candles(symbol=symbol, timeframe=tf)
        indicators = calculate_indicators(candles)
        signal = generate_signal(indicators, symbol, tf)

        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="back")]])
        await query.edit_message_text(text=signal, reply_markup=back_button, parse_mode="Markdown")
        return

# авто-сигналы (по 15m)
def auto_job():
    results = []
    for symbol in COINS.keys():
        candles = get_candles(symbol=symbol, timeframe="15m")
        indicators = calculate_indicators(candles)
        results.append(generate_signal(indicators, symbol, "15m"))

    time_now = datetime.now(TIMEZONE).strftime("%H:%M %d-%m-%Y")
    message = f"📢 *Авто-сигналы ({time_now})*\n\n" + "\n".join(results)
    send_message(message)

def run_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("signals", start))
    app.add_handler(CallbackQueryHandler(button))

    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(auto_job, "interval", minutes=15)
    scheduler.start()

    print("🤖 Бот запущен (Bybit). Используй /signals для запуска вручную.")
    app.run_polling()
