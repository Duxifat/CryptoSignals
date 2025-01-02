import asyncio
import sys
from gui.trading_app import TradingApp
from utils.logging_utils import setup_logging

# Устанавливаем SelectorEventLoop для Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def main():
    # Настройка логирования
    setup_logging()

    # Создание и запуск приложения
    app = TradingApp()
    app.mainloop()

if __name__ == "__main__":
    main()