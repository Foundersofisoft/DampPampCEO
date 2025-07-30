import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot.handlers import run_bot

if __name__ == "__main__":
    run_bot()
