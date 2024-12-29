import pandas as pd
import ccxt
import logging
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timezone

class DataFetcher:
    def __init__(self):
        """
        Initialize DataFetcher with connections to Bybit exchange.
        """
        try:
            # Инициализация Bybit с API-ключами и увеличенным recv_window
            self.bybit = ccxt.bybit({
                'apiKey': '49lPvpiehnX70223eL',  # Ваш API-ключ
                'secret': 'yD8GAvgQPyA5K867WjXgIQEf86NbYphr2Rh2',  # Ваш Secret-ключ
                'options': {
                    'recvWindow': 15000,  # Увеличенное значение recv_window
                },
            })
            logging.info("Bybit API initialized successfully.")
            # Проверка времени сразу после инициализации
            self.check_time_synchronization()
        except Exception as e:
            logging.error(f"Error initializing Bybit API: {e}")
            raise

    def check_time_synchronization(self):
        """
        Check if the local time is synchronized with the server time.
        If not synchronized, warn the user.
        """
        try:
            # Получение времени сервера Bybit
            server_time_ms = self.bybit.fetch_time()  # Время в миллисекундах
            server_time = datetime.fromtimestamp(server_time_ms / 1000.0, tz=timezone.utc)
            local_time = datetime.now(timezone.utc)
            time_difference = abs((local_time - server_time).total_seconds())

            # Если разница времени превышает 5 секунд, предупреждаем пользователя
            if time_difference > 5:
                self.show_time_warning(time_difference)
        except Exception as e:
            logging.error(f"Error checking time synchronization: {e}")
            raise RuntimeError("Unable to check time synchronization.")

    def show_time_warning(self, time_difference):
        """
        Show a warning message if the local time is out of sync.
        """
        try:
            root = tk.Tk()
            root.withdraw()  # Скрыть главное окно
            messagebox.showwarning(
                "Проблема синхронизации времени",
                f"Разница между локальным временем и временем сервера составляет {time_difference:.2f} секунд.\n"
                "Пожалуйста, установите точное время на вашем компьютере.\n"
                "Без этого программа работать не будет."
            )
            root.destroy()
        except Exception as e:
            logging.error(f"Error showing time warning: {e}")
        finally:
            # Остановка программы
            raise RuntimeError("Local time is not synchronized with server time.")

    def fetch_historical_data(self, symbol, timeframe='1h', limit=200):
        """
        Fetch historical OHLCV data for a given symbol and timeframe.
        :param symbol: Trading pair (e.g., BTC/USDT)
        :param timeframe: Timeframe for data (e.g., '1h', '4h')
        :param limit: Number of data points to fetch
        :return: DataFrame with OHLCV data
        """
        try:
            ohlcv = self.bybit.fetch_ohlcv(symbol, timeframe, limit=limit)
            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('timestamp', inplace=True)

            logging.info(f"Historical data for {symbol} ({timeframe}) fetched successfully.")
            return data
        except ccxt.BaseError as e:
            logging.error(f"Bybit API error fetching historical data for {symbol} ({timeframe}): {e}")
        except Exception as e:
            logging.error(f"Error fetching historical data for {symbol} ({timeframe}): {e}")
        return pd.DataFrame()
