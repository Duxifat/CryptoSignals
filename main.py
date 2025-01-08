# ========== main.py ==========

import asyncio
import sys
from gui.trading_app import TradingApp
from utils.logging_utils import setup_logging

# Единственное исправление:
# Устанавливаем SelectorEventLoopPolicy на Windows,
# чтобы aiodns мог корректно работать с asyncio.
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def main():
    # Настройка логирования
    setup_logging()

    # Создание и запуск приложения (GUI)
    app = TradingApp()
    app.mainloop()

if __name__ == "__main__":
    main()
