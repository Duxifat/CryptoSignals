import pandas as pd

class Supertrend:
    @staticmethod
    def get_signal(data):
        return "Покупать" if data["close"].iloc[-1] > data["close"].mean() else "Продавать"

class EMA:
    @staticmethod
    def get_signal(data):
        short_ema = data["close"].ewm(span=9).mean().iloc[-1]
        long_ema = data["close"].ewm(span=21).mean().iloc[-1]
        return "Покупать" if short_ema > long_ema else "Продавать"

class RSI:
    @staticmethod
    def get_signal(data):
        delta = data["close"].diff()
        gain = (delta.where(delta > 0, 0)).mean()
        loss = (-delta.where(delta < 0, 0)).mean()
        rs = gain / loss if loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        return "Перекупленность" if rsi > 70 else "Перепроданность" if rsi < 30 else "Нейтрально"

class MACD:
    @staticmethod
    def get_signal(data):
        short_ema = data["close"].ewm(span=12).mean()
        long_ema = data["close"].ewm(span=26).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=9).mean()
        return "Покупать" if macd.iloc[-1] > signal.iloc[-1] else "Продавать"