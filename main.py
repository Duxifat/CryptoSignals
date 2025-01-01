from gui.trading_app import TradingApp
from utils.logging_utils import setup_logging

def main():
    # Настройка логирования
    setup_logging()

    # Создание и запуск приложения
    app = TradingApp()
    app.mainloop()

if __name__ == "__main__":
    main()