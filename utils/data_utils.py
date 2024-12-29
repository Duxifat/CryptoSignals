import pandas as pd
import logging

def filter_outliers(data, window=5, threshold=0.5):
    """
    Remove outliers from data based on rolling mean, standard deviation, and hard thresholds.
    """
    try:
        mean = data['close'].rolling(window=window, min_periods=1).mean()
        std = data['close'].rolling(window=window, min_periods=1).std()

        # Логируем границы
        logging.info(f"Mean + 3*STD (first 5):\n{(mean + 3 * std).head()}")
        logging.info(f"Mean - 3*STD (first 5):\n{(mean - 3 * std).head()}")

        # Условия для определения выбросов
        mask = ((data['close'] > mean + 3 * std) | (data['close'] < mean - 3 * std))

        # Добавляем жесткие пороговые границы
        hard_threshold_high = 120  # Жесткая верхняя граница
        hard_threshold_low = 80    # Жесткая нижняя граница
        logging.info(f"Hard thresholds: {hard_threshold_low} - {hard_threshold_high}")
        hard_mask = (data['close'] > hard_threshold_high) | (data['close'] < hard_threshold_low)

        # Объединяем маски
        mask = mask | hard_mask
        mask = mask.fillna(False)

        # Логируем выбросы
        outliers = data[mask]
        logging.info(f"Outliers detected:\n{outliers}")

        # Удаление выбросов
        data.loc[mask, ['open', 'high', 'low', 'close', 'volume']] = None
        data.dropna(inplace=True)

        return data
    except Exception as e:
        logging.error(f"Error: {e}")
        return data