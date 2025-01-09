# ========== strategies.py ==========

import backtrader as bt
from utils.indicators import Supertrend, MACD, ATR

class ShortTermStrategy(bt.Strategy):
    """
    Стратегия для краткосрочной торговли.
    Основной акцент на индикаторы: EMA, RSI, Supertrend, MACD.
    """
    params = (
        ('ema_period', 20),
        ('rsi_period', 14),
        ('atr_period', 14),
        ('supertrend_period', 10),
        ('supertrend_multiplier', 3),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
    )

    def __init__(self):
        # Индикаторы для краткосрочной торговли
        self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.atr = ATR(self.data, period=self.params.atr_period)
        self.supertrend = Supertrend(self.data, period=self.params.supertrend_period, multiplier=self.params.supertrend_multiplier)
        self.macd = MACD(self.data, fast=self.params.macd_fast, slow=self.params.macd_slow, signal=self.params.macd_signal)

    def next(self):
        """
        Логика для краткосрочной торговли.
        """
        # Условие для покупки
        if (self.supertrend.lines.direction[0] == 1 and  # Supertrend указывает на рост
            self.rsi[0] < 30 and  # RSI в зоне перепроданности
            self.data.close[0] > self.ema[0] and  # Цена выше EMA
            self.macd.lines.macd[0] > self.macd.lines.signal[0]):  # MACD выше сигнальной линии
            self.buy()

        # Условие для продажи
        elif (self.supertrend.lines.direction[0] == -1 and  # Supertrend указывает на спад
              self.rsi[0] > 70 and  # RSI в зоне перекупленности
              self.data.close[0] < self.ema[0] and  # Цена ниже EMA
              self.macd.lines.macd[0] < self.macd.lines.signal[0]):  # MACD ниже сигнальной линии
            self.sell()


class MidTermStrategy(bt.Strategy):
    """
    Стратегия для среднесрочной торговли.
    Основной акцент на долгосрочные индикаторы: EMA, Supertrend, ATR.
    """
    params = (
        ('ema_period', 50),
        ('atr_period', 14),
        ('supertrend_period', 20),
        ('supertrend_multiplier', 3),
    )

    def __init__(self):
        # Индикаторы для среднесрочной торговли
        self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        self.atr = ATR(self.data, period=self.params.atr_period)
        self.supertrend = Supertrend(self.data, period=self.params.supertrend_period, multiplier=self.params.supertrend_multiplier)

    def next(self):
        """
        Логика для среднесрочной торговли.
        """
        # Условие для покупки
        if (self.supertrend.lines.direction[0] == 1 and  # Supertrend указывает на рост
            self.data.close[0] > self.ema[0]):  # Цена выше EMA
            self.buy()

        # Условие для продажи
        elif (self.supertrend.lines.direction[0] == -1 and  # Supertrend указывает на спад
              self.data.close[0] < self.ema[0]):  # Цена ниже EMA
            self.sell()