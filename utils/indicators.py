import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, List
from utils.logging_utils import log_event

class Supertrend:
    @staticmethod
    def get_signal(data: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> str:
        """
        Возвращает сигнал Supertrend.
        :param data: DataFrame с данными OHLCV.
        :param period: Период для расчета ATR.
        :param multiplier: Множитель для расчета Supertrend.
        :return: Сигнал ("Покупать", "Продавать" или "Нейтрально").
        """
        try:
            if data is None or data.empty:
                raise ValueError("Data is None or empty.")

            # Расчет ATR
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()

            # Расчет Supertrend
            hl2 = (data['high'] + data['low']) / 2
            upper_band = hl2 + (multiplier * atr)
            lower_band = hl2 - (multiplier * atr)

            supertrend = pd.Series(index=data.index, dtype=float)
            direction = pd.Series(index=data.index, dtype=int)

            for i in range(1, len(data)):
                if data['close'][i] > upper_band[i - 1]:
                    supertrend[i] = lower_band[i]
                    direction[i] = 1  # Бычий тренд
                elif data['close'][i] < lower_band[i - 1]:
                    supertrend[i] = upper_band[i]
                    direction[i] = -1  # Медвежий тренд
                else:
                    supertrend[i] = supertrend[i - 1]
                    direction[i] = direction[i - 1]

            # Определение сигнала
            if direction.iloc[-1] == 1:
                return "Покупать"
            elif direction.iloc[-1] == -1:
                return "Продавать"
            else:
                return "Нейтрально"
        except Exception as e:
            log_event("Indicator Error", f"Error calculating Supertrend: {e}", level="error")
            return "Нейтрально"

class EMA:
    @staticmethod
    def get_signal(data: pd.DataFrame, short_period: int = 9, long_period: int = 21) -> str:
        """
        Возвращает сигнал EMA.
        :param data: DataFrame с данными OHLCV.
        :param short_period: Период для короткой EMA.
        :param long_period: Период для длинной EMA.
        :return: Сигнал ("Покупать" или "Продавать").
        """
        try:
            if data is None or data.empty:
                raise ValueError("Data is None or empty.")

            short_ema = data['close'].ewm(span=short_period, adjust=False).mean()
            long_ema = data['close'].ewm(span=long_period, adjust=False).mean()

            if short_ema.iloc[-1] > long_ema.iloc[-1]:
                return "Покупать"
            else:
                return "Продавать"
        except Exception as e:
            log_event("Indicator Error", f"Error calculating EMA: {e}", level="error")
            return "Нейтрально"

class RSI:
    @staticmethod
    def get_signal(data: pd.DataFrame, period: int = 14, overbought: float = 70, oversold: float = 30) -> str:
        """
        Возвращает сигнал RSI.
        :param data: DataFrame с данными OHLCV.
        :param period: Период для расчета RSI.
        :param overbought: Уровень перекупленности.
        :param oversold: Уровень перепроданности.
        :return: Сигнал ("Перекупленность", "Перепроданность" или "Нейтрально").
        """
        try:
            if data is None or data.empty:
                raise ValueError("Data is None or empty.")

            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            if rsi.iloc[-1] > overbought:
                return "Перекупленность"
            elif rsi.iloc[-1] < oversold:
                return "Перепроданность"
            else:
                return "Нейтрально"
        except Exception as e:
            log_event("Indicator Error", f"Error calculating RSI: {e}", level="error")
            return "Нейтрально"

class MACD:
    @staticmethod
    def get_signal(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> str:
        """
        Возвращает сигнал MACD.
        :param data: DataFrame с данными OHLCV.
        :param fast_period: Период для быстрой EMA.
        :param slow_period: Период для медленной EMA.
        :param signal_period: Период для сигнальной линии.
        :return: Сигнал ("Покупать" или "Продавать").
        """
        try:
            if data is None or data.empty:
                raise ValueError("Data is None or empty.")

            fast_ema = data['close'].ewm(span=fast_period, adjust=False).mean()
            slow_ema = data['close'].ewm(span=slow_period, adjust=False).mean()
            macd = fast_ema - slow_ema
            signal = macd.ewm(span=signal_period, adjust=False).mean()

            if macd.iloc[-1] > signal.iloc[-1]:
                return "Покупать"
            else:
                return "Продавать"
        except Exception as e:
            log_event("Indicator Error", f"Error calculating MACD: {e}", level="error")
            return "Нейтрально"

class ATR:
    @staticmethod
    def get_atr(data: pd.DataFrame, period: int = 14) -> float:
        """
        Возвращает значение ATR.
        :param data: DataFrame с данными OHLCV.
        :param period: Период для расчета ATR.
        :return: Значение ATR.
        """
        try:
            if data is None or data.empty:
                raise ValueError("Data is None or empty.")

            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            return atr.iloc[-1]
        except Exception as e:
            log_event("Indicator Error", f"Error calculating ATR: {e}", level="error")
            return 0.0

class BollingerBands:
    @staticmethod
    def get_signal(data: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> str:
        """
        Возвращает сигнал на основе Bollinger Bands.
        :param data: DataFrame с данными OHLCV.
        :param period: Период для расчета SMA.
        :param multiplier: Множитель для стандартного отклонения.
        :return: Сигнал ("Покупать", "Продавать" или "Нейтрально").
        """
        try:
            if data is None or data.empty:
                raise ValueError("Data is None or empty.")

            sma = data['close'].rolling(window=period).mean()
            std = data['close'].rolling(window=period).std()
            upper_band = sma + (multiplier * std)
            lower_band = sma - (multiplier * std)

            if data['close'].iloc[-1] > upper_band.iloc[-1]:
                return "Продавать"
            elif data['close'].iloc[-1] < lower_band.iloc[-1]:
                return "Покупать"
            else:
                return "Нейтрально"
        except Exception as e:
            log_event("Indicator Error", f"Error calculating Bollinger Bands: {e}", level="error")
            return "Нейтрально"