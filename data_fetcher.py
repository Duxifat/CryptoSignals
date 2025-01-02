import os
import pandas as pd
import ccxt
import logging
from datetime import datetime, timezone
import tkinter as tk
from tkinter import messagebox
import aiohttp
import asyncio

class DataFetcher:
    def __init__(self):
        """
        Initialize DataFetcher with connections to Bybit exchange.
        """
        try:
            # Инициализация Bybit с вашим API-ключом и секретом
            self.bybit = ccxt.bybit({
                'apiKey': '49lPvpiehnX70223eL',  # Ваш API KEY
                'secret': 'yD8GAvgQPyA5K867WjXgIQEf86NbYphr2Rh2',  # Ваш API Secret
                'options': {
                    'recvWindow': 15000,  # Увеличенное значение recv_window
                },
            })
            logging.info("Bybit API initialized successfully.")

            # Проверка синхронизации времени
            self.check_time_synchronization()

        except ccxt.NetworkError as e:
            logging.error(f"Network error during initialization: {e}")
            raise RuntimeError("Ошибка сети. Пожалуйста, проверьте интернет-соединение.")
        except ccxt.ExchangeError as e:
            logging.error(f"Exchange error during initialization: {e}")
            raise RuntimeError("Ошибка биржи. Пожалуйста, проверьте API ключи и разрешения.")
        except Exception as e:
            logging.error(f"Unexpected error during initialization: {e}")
            raise RuntimeError("Произошла непредвиденная ошибка.")

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
            raise RuntimeError("Не удалось проверить синхронизацию времени.")

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
            raise RuntimeError("Локальное время не синхронизировано с серверным временем.")

    async def fetch_historical_data_async(self, symbol, timeframe='60', limit=200):
        """
        Fetch historical OHLCV data for a given symbol and timeframe asynchronously.
        :param symbol: Trading pair (e.g., BTCUSDT)
        :param timeframe: Timeframe for data (e.g., '60' for 1 hour, 'D' for daily)
        :param limit: Number of data points to fetch
        :return: DataFrame with OHLCV data
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}&interval={timeframe}&limit={limit}"
                async with session.get(url) as response:
                    if response.status != 200:
                        error_message = await response.text()
                        raise ValueError(f"HTTP {response.status}: {error_message}")
                    data = await response.json()
                    if data['retCode'] != 0:
                        raise ValueError(f"Error fetching data: {data['retMsg']}")
                    ohlcv = data['result']['list']
                    # Убедитесь, что количество столбцов соответствует данным
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'extra'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    logging.info(f"Historical data for {symbol} ({timeframe}) fetched successfully.")
                    return df
        except Exception as e:
            logging.error(f"Error fetching data for {symbol} ({timeframe}): {e}")
            return pd.DataFrame()
        finally:
            await asyncio.sleep(1)  # Задержка между запросами

    def fetch_historical_data(self, symbol, timeframe='1h', limit=200):
        """
        Fetch historical OHLCV data for a given symbol and timeframe synchronously.
        :param symbol: Trading pair (e.g., BTCUSDT)
        :param timeframe: Timeframe for data (e.g., '1h', '4h')
        :param limit: Number of data points to fetch
        :return: DataFrame with OHLCV data
        """
        try:
            ohlcv = self.bybit.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                logging.error(f"No data returned for {symbol} ({timeframe}).")
                return pd.DataFrame()
            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('timestamp', inplace=True)
            logging.info(f"Historical data for {symbol} ({timeframe}) fetched successfully.")
            return data
        except ccxt.NetworkError as e:
            logging.error(f"Network error fetching data for {symbol} ({timeframe}): {e}")
            raise RuntimeError("Ошибка сети. Пожалуйста, проверьте интернет-соединение.")
        except ccxt.ExchangeError as e:
            logging.error(f"Exchange error fetching data for {symbol} ({timeframe}): {e}")
            raise RuntimeError("Ошибка биржи. Пожалуйста, проверьте API ключи и разрешения.")
        except Exception as e:
            logging.error(f"Unexpected error fetching data for {symbol} ({timeframe}): {e}")
            raise RuntimeError("Произошла непредвиденная ошибка.")