from telegram import Bot
from config import TELEGRAM_TOKEN, CHAT_ID
import asyncio

bot = Bot(token=TELEGRAM_TOKEN)

async def send_message_async(text, chat_id=CHAT_ID):
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        await asyncio.sleep(0.5)  # чтобы не перегружать Telegram API
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

def send_message(text, chat_id=CHAT_ID):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(send_message_async(text, chat_id))
        else:
            loop.run_until_complete(send_message_async(text, chat_id))
    except RuntimeError:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send_message_async(text, chat_id))
