import pandas as pd
import logging

def filter_outliers(data, window=5, threshold=0.5):
    try:
        mean = data['close'].rolling(window=window, min_periods=1).mean()
        std = data['close'].rolling(window=window, min_periods=1).std()
        mask = ((data['close'] > mean + 3 * std) | (data['close'] < mean - 3 * std))
        data.loc[mask, ['open', 'high', 'low', 'close', 'volume']] = None
        data.dropna(inplace=True)
        return data
    except Exception as e:
        logging.error(f"Error filtering outliers: {e}")
        return data