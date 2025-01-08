import os
import pandas as pd
import ccxt
import logging
from datetime import datetime, timezone
import tkinter as tk
from tkinter import messagebox
import aiohttp
import asyncio
import json
from typing import Optional, Dict, List
from utils.logging_utils import log_data_fetching, log_data_fetching_error

class DataFetcher:
    def __init__(self, cache_dir: str = "data_cache"):
        """
        Инициализация DataFetcher с подключением к Bybit.
        :param cache_dir: Директория для кэширования данных.
        """
        self.cache_dir = cache_dir
        self._ensure_cache_dir_exists()

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

    def _ensure_cache_dir_exists(self):
        """Создает директорию для кэширования данных, если она не существует."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_file_path(self, symbol: str, timeframe: str) -> str:
        """
        Возвращает путь к файлу кэша для указанной пары и таймфрейма.
        :param symbol: Торговая пара (например, BTCUSDT).
        :param timeframe: Таймфрейм (например, '1h').
        :return: Путь к файлу кэша.
        """
        return os.path.join(self.cache_dir, f"{symbol}_{timeframe}.json")

    def _load_from_cache(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Загружает данные из кэша, если они есть.
        :param symbol: Торговая пара.
        :param timeframe: Таймфрейм.
        :return: DataFrame с данными или None, если кэш отсутствует или битый.
        """
        cache_file = self._get_cache_file_path(symbol, timeframe)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                df = pd.DataFrame(data)

                # -- Добавляем обработку KeyError при отсутствии 'timestamp'
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
                except KeyError:  # <-- ADD
                    logging.error(f"Missing 'timestamp' in the file {cache_file}")
                    return None  # или pd.DataFrame()

                df.set_index('timestamp', inplace=True)
                logging.info(f"Loaded cached data for {symbol} ({timeframe}).")
                return df
            except Exception as e:
                logging.error(f"Error loading cache for {symbol} ({timeframe}): {e}")
        return None

    def _save_to_cache(self, symbol: str, timeframe: str, data: pd.DataFrame):
        """
        Сохраняет данные в кэш.
        :param symbol: Торговая пара.
        :param timeframe: Таймфрейм.
        :param data: DataFrame с данными.
        """
        cache_file = self._get_cache_file_path(symbol, timeframe)
        try:
            data.to_json(cache_file, orient='records')
            logging.info(f"Saved data to cache for {symbol} ({timeframe}).")
        except Exception as e:
            logging.error(f"Error saving cache for {symbol} ({timeframe}): {e}")

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

    def show_time_warning(self, time_difference: float):
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

    async def fetch_historical_data_async(self, symbol: str, timeframe: str = '60', limit: int = 200) -> pd.DataFrame:
        """
        Получает исторические данные для указанного символа и таймфрейма асинхронно.
        :param symbol: Торговая пара (например, BTCUSDT).
        :param timeframe: Таймфрейм (например, '1' для 1 минуты, '60' для 1 часа).
        :param limit: Количество свечей.
        :return: DataFrame с данными OHLCV.
        """
        try:
            # Проверяем кэш
            cached_data = self._load_from_cache(symbol, timeframe)
            if cached_data is not None:
                return cached_data

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
                    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
                    df.set_index('timestamp', inplace=True)

                    # Сохраняем данные в кэш
                    self._save_to_cache(symbol, timeframe, df)

                    log_data_fetching(symbol, timeframe)
                    return df
        except Exception as e:
            log_data_fetching_error(symbol, timeframe, e)
            return pd.DataFrame()
        finally:
            await asyncio.sleep(1)  # Задержка между запросами

    def fetch_historical_data(self, symbol: str, timeframe: str = '1h', limit: int = 200) -> pd.DataFrame:
        """
        Получает исторические данные для указанного символа и таймфрейма синхронно.
        :param symbol: Торговая пара (например, BTCUSDT).
        :param timeframe: Таймфрейм (например, '1h', '4h').
        :param limit: Количество свечей.
        :return: DataFrame с данными OHLCV.
        """
        try:
            # Проверяем кэш
            cached_data = self._load_from_cache(symbol, timeframe)
            if cached_data is not None:
                return cached_data

            ohlcv = self.bybit.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                logging.error(f"No data returned for {symbol} ({timeframe}).")
                return pd.DataFrame()
            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'].astype(float), unit='ms')
            data.set_index('timestamp', inplace=True)

            # Сохраняем данные в кэш
            self._save_to_cache(symbol, timeframe, data)

            log_data_fetching(symbol, timeframe)
            return data
        except ccxt.NetworkError as e:
            log_data_fetching_error(symbol, timeframe, e)
            raise RuntimeError("Ошибка сети. Пожалуйста, проверьте интернет-соединение.")
        except ccxt.ExchangeError as e:
            log_data_fetching_error(symbol, timeframe, e)
            raise RuntimeError("Ошибка биржи. Пожалуйста, проверьте API ключи и разрешения.")
        except Exception as e:
            log_data_fetching_error(symbol, timeframe, e)
            raise RuntimeError("Произошла непредвиденная ошибка.")
