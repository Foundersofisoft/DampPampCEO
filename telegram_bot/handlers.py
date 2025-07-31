from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from core.bybit_api import get_candles
from core.indicators import calculate_indicators
from core.strategy import generate_signal, check_hot_signal
from core.charts import create_chart
from core.alerts import add_alert, check_alerts
from telegram_bot.notifier import send_message
from config import TELEGRAM_TOKEN, CHAT_ID
import pytz
from datetime import datetime
import requests
import asyncio

TIMEZONE = pytz.timezone("Asia/Almaty")
user_settings = {}

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
    "ARB/USDT": "🌀 ARB",
    "APT/USDT": "🌐 APT",
}

TIMEFRAMES = {
    "5m": "⏱ 5m",
    "15m": "⏱ 15m",
    "1h": "🕒 1h",
    "4h": "🕓 4h",
}

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 Сигналы", callback_data="menu_signals")],
        [InlineKeyboardButton("🔔 Алерты", callback_data="menu_alerts")],
        [InlineKeyboardButton("📰 Новости", callback_data="menu_news")],
        [InlineKeyboardButton("⚙ Настройки", callback_data="menu_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_menu():
    keyboard = [
        [InlineKeyboardButton("🌍 Таймзона", callback_data="settings_timezone")],
        [InlineKeyboardButton("⏱ Интервал авто-сигналов", callback_data="settings_interval")],
        [InlineKeyboardButton("🔥 Фильтр сигналов", callback_data="settings_filter")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_timezone_menu():
    keyboard = [
        [InlineKeyboardButton("Asia/Almaty", callback_data="tz|Asia/Almaty")],
        [InlineKeyboardButton("Europe/Moscow", callback_data="tz|Europe/Moscow")],
        [InlineKeyboardButton("UTC", callback_data="tz|UTC")],
        [InlineKeyboardButton("⬅ Назад", callback_data="menu_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_interval_menu():
    keyboard = [
        [InlineKeyboardButton("5 мин", callback_data="int|5")],
        [InlineKeyboardButton("15 мин", callback_data="int|15")],
        [InlineKeyboardButton("30 мин", callback_data="int|30")],
        [InlineKeyboardButton("60 мин", callback_data="int|60")],
        [InlineKeyboardButton("⬅ Назад", callback_data="menu_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_filter_menu():
    keyboard = [
        [InlineKeyboardButton("Все сигналы", callback_data="filter|all")],
        [InlineKeyboardButton("🔥 Только сочные", callback_data="filter|hot")],
        [InlineKeyboardButton("⬅ Назад", callback_data="menu_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    real_chat_id = update.message.chat_id
    print(f"[DEBUG] Real Chat ID: {real_chat_id}")
    user_settings[real_chat_id] = {
        "timezone": "Asia/Almaty",
        "interval": 15,
        "filter": "all",
        "alert_symbol": None,
        "alert_price": None
    }
    await update.message.reply_text("👋 Добро пожаловать! Выберите раздел:", reply_markup=get_main_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    chat_id = query.message.chat_id

    # ===== Главное меню =====
    if query.data == "back_menu":
        await query.edit_message_text("👋 Добро пожаловать! Выберите раздел:", reply_markup=get_main_menu())
        return

    if query.data == "menu_signals":
        keyboard = [[InlineKeyboardButton(f"{emoji}", callback_data=f"coin|{symbol}")]
                    for symbol, emoji in COINS.items()]
        keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="back_menu")])
        await query.edit_message_text("📊 Выберите монету:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "menu_alerts":
        keyboard = [[InlineKeyboardButton(f"{emoji}", callback_data=f"alert_coin|{symbol}")]
                    for symbol, emoji in COINS.items()]
        keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="back_menu")])
        await query.edit_message_text("🔔 Выберите монету для алерта:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "menu_news":
        news = get_crypto_news()
        await query.edit_message_text(
            f"📰 Новости:\n\n{news}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="back_menu")]])
        )
        return

    if query.data == "menu_settings":
        await query.edit_message_text("⚙ Настройки:", reply_markup=get_settings_menu())
        return

    # ===== Настройки =====
    if query.data == "settings_timezone":
        await query.edit_message_text("🌍 Выбери таймзону:", reply_markup=get_timezone_menu())
        return

    if data[0] == "tz":
        user_settings[chat_id]["timezone"] = data[1]
        await query.edit_message_text(f"✅ Таймзона изменена на {data[1]}", reply_markup=get_settings_menu())
        return

    if query.data == "settings_interval":
        await query.edit_message_text("⏱ Установи интервал авто-сигналов:", reply_markup=get_interval_menu())
        return

    if data[0] == "int":
        user_settings[chat_id]["interval"] = int(data[1])
        await query.edit_message_text(f"✅ Интервал авто-сигналов: {data[1]} мин", reply_markup=get_settings_menu())
        return

    if query.data == "settings_filter":
        await query.edit_message_text("🔥 Выбери фильтр сигналов:", reply_markup=get_filter_menu())
        return

    if data[0] == "filter":
        user_settings[chat_id]["filter"] = data[1]
        await query.edit_message_text(f"✅ Фильтр сигналов: {data[1]}", reply_markup=get_settings_menu())
        return

    # ===== Алерты =====
    if data[0] == "alert_coin":
        user_settings[chat_id]["alert_symbol"] = data[1]
        await query.edit_message_text(f"Введи цену для {data[1]} через команду /alert {data[1]} 65000",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="menu_alerts")]]))
        return

    # ===== Сигналы =====
    if data[0] == "coin":
        symbol = data[1]
        keyboard = [[InlineKeyboardButton(f"{emoji}", callback_data=f"tf|{symbol}|{tf}")]
                    for tf, emoji in TIMEFRAMES.items()]
        keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="menu_signals")])
        await query.edit_message_text(f"⏱ Выбери таймфрейм для {symbol}:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data[0] == "tf":
        symbol = data[1]
        tf = data[2]
        candles = get_candles(symbol=symbol, timeframe=tf)
        indicators = calculate_indicators(candles)
        signal = generate_signal(indicators, symbol, tf)
        chart = create_chart(indicators['df'], symbol)

        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="menu_signals")]])
        await query.message.reply_photo(photo=InputFile(chart, filename=f"{symbol}.png"))
        await query.edit_message_text(text=signal, reply_markup=back_button, parse_mode="Markdown")

# ===== Автопостинг =====
def auto_job():
    time_now = datetime.now(TIMEZONE).strftime("%H:%M %d-%m-%Y")
    header = f"📢 Авто-сигналы ({time_now})\n\n"
    results = []

    for symbol in COINS.keys():
        candles = get_candles(symbol=symbol, timeframe="15m")
        indicators = calculate_indicators(candles)
        if user_settings and list(user_settings.values())[0]["filter"] == "all" or check_hot_signal(indicators):
            results.append(generate_signal(indicators, symbol, "15m"))

    if results:
        message = header + "\n".join(results)
        send_message(message, chat_id=CHAT_ID)
        print(f"[AUTO_JOB] {len(results)} сигналов отправлено в чат {CHAT_ID}")

def hot_signals():
    for symbol in COINS.keys():
        candles = get_candles(symbol=symbol, timeframe="15m")
        indicators = calculate_indicators(candles)
        if check_hot_signal(indicators):
            signal = generate_signal(indicators, symbol, "15m")
            send_message("🔥 Сочный сигнал!\n" + signal, chat_id=CHAT_ID)
            print(f"[HOT_SIGNAL] Сигнал для {symbol} отправлен в {CHAT_ID}")

def get_crypto_news():
    try:
        url = "https://api.coingecko.com/api/v3/news"
        res = requests.get(url)
        articles = res.json().get("data", [])[:5]
        news = ""
        for art in articles:
            news += f"🔗 {art['title']} ({art['url']})\n\n"
        return news if news else "⚠️ Новости не найдены."
    except Exception as e:
        return f"❌ Ошибка загрузки новостей: {e}"

def run_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("alert", set_alert))
    app.add_handler(CallbackQueryHandler(button))

    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(auto_job, "interval", minutes=15)
    scheduler.add_job(hot_signals, "interval", minutes=1)
    scheduler.add_job(check_alerts, "interval", minutes=2)
    scheduler.start()

    auto_job()
    print("🤖 Бот запущен. Авто-сигналы и горячие сигналы → группа.")
    app.run_polling()

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0]
        price = float(context.args[1])
        response = add_alert(update.message.chat_id, symbol, price)
        await update.message.reply_text(response)
    except:
        await update.message.reply_text("⚠ Используй: /alert BTC/USDT 65000")