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
        Инициализация DataFetcher с подключением к Bybit.
        """
        try:
            # Инициализация Bybit с API-ключом и секретом
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
        Проверяет синхронизацию локального времени с серверным временем Bybit.
        Если разница больше 5 секунд, выводит предупреждение.
        """
        try:
            server_time_ms = self.bybit.fetch_time()  # Время в миллисекундах
            server_time = datetime.fromtimestamp(server_time_ms / 1000.0, tz=timezone.utc)
            local_time = datetime.now(timezone.utc)
            time_difference = abs((local_time - server_time).total_seconds())

            if time_difference > 5:
                self.show_time_warning(time_difference)
        except Exception as e:
            logging.error(f"Error checking time synchronization: {e}")
            raise RuntimeError("Не удалось проверить синхронизацию времени.")

    def show_time_warning(self, time_difference):
        """
        Показывает предупреждение, если локальное время не синхронизировано с серверным.
        :param time_difference: Разница во времени в секундах.
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
            raise RuntimeError("Локальное время не синхронизировано с серверным временем.")

    async def fetch_historical_data_async(self, symbol, timeframe='60', limit=200):
        """
        Получает исторические данные для указанного символа и таймфрейма асинхронно.
        :param symbol: Торговая пара (например, BTCUSDT).
        :param timeframe: Таймфрейм (например, '1' для 1 минуты, '60' для 1 часа).
        :param limit: Количество свечей.
        :return: DataFrame с данными OHLCV.
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
        Получает исторические данные для указанного символа и таймфрейма синхронно.
        :param symbol: Торговая пара (например, BTCUSDT).
        :param timeframe: Таймфрейм (например, '1h', '4h').
        :param limit: Количество свечей.
        :return: DataFrame с данными OHLCV.
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