import backtrader as bt
from utils.indicators import Supertrend, MACD, ATR

class MyStrategy(bt.Strategy):
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
        self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.atr = ATR(self.data, period=self.params.atr_period)
        self.supertrend = Supertrend(self.data, period=self.params.supertrend_period, multiplier=self.params.supertrend_multiplier)
        self.macd = MACD(self.data, fast=self.params.macd_fast, slow=self.params.macd_slow, signal=self.params.macd_signal)

    def next(self):
        if self.supertrend.lines.direction[0] == 1 and self.rsi[0] < 30 and self.data.close[0] > self.ema[0]:
            self.buy()
        elif self.supertrend.lines.direction[0] == -1 and self.rsi[0] > 70 and self.data.close[0] < self.ema[0]:
            self.sell()