import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, List
from utils.logging_utils import log_event

def validate_data(data: pd.DataFrame, check_outliers: bool = True, outlier_threshold: float = 3.0) -> bool:
    """
    Проверяет данные на корректность.
    :param data: Данные для проверки.
    :param check_outliers: Флаг для проверки на выбросы.
    :param outlier_threshold: Порог для определения выбросов (в стандартных отклонениях).
    :return: True, если данные корректны, иначе False.
    """
    try:
        # Проверка на пустые данные
        if data is None or data.empty:
            log_event("Data Validation", "Data validation failed: Data is None or empty.", level="warning")
            return False

        # Проверка типа данных
        if not isinstance(data, pd.DataFrame):
            log_event("Data Validation", "Data validation failed: Data is not a pandas DataFrame.", level="warning")
            return False

        # Проверка на отсутствие значений
        if data.isnull().any().any():
            log_event("Data Validation", "Data validation failed: Missing values detected.", level="warning")
            return False

        # Проверка наличия обязательных столбцов
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            log_event("Data Validation", f"Data validation failed: Missing required columns. Expected: {required_columns}", level="warning")
            return False

        # Проверка на выбросы (опционально)
        if check_outliers:
            for column in ['open', 'high', 'low', 'close']:
                mean = data[column].mean()
                std = data[column].std()
                outliers = data[(data[column] > mean + outlier_threshold * std) | (data[column] < mean - outlier_threshold * std)]
                if not outliers.empty:
                    log_event("Data Validation", f"Data validation warning: Outliers detected in column '{column}'.", level="warning")

        # Проверка на корректность значений
        if (data['high'] < data['low']).any():
            log_event("Data Validation", "Data validation failed: High values are less than low values.", level="warning")
            return False

        if (data['close'] < 0).any() or (data['volume'] < 0).any():
            log_event("Data Validation", "Data validation failed: Negative values detected in 'close' or 'volume'.", level="warning")
            return False

        log_event("Data Validation", "Data validation successful.")
        return True

    except Exception as e:
        log_event("Data Validation", f"Error during data validation: {e}", level="error")
        return False

def detect_anomalies(data: pd.DataFrame, threshold: float = 3.0) -> Dict[str, List[int]]:
    """
    Обнаруживает аномалии в данных на основе статистических методов.
    :param data: Данные для анализа.
    :param threshold: Порог для определения аномалий (в стандартных отклонениях).
    :return: Словарь с аномалиями для каждого столбца.
    """
    anomalies = {}
    try:
        for column in ['open', 'high', 'low', 'close', 'volume']:
            mean = data[column].mean()
            std = data[column].std()
            anomalies[column] = data[(data[column] > mean + threshold * std) | (data[column] < mean - threshold * std)].index.tolist()
    except Exception as e:
        log_event("Anomaly Detection", f"Error detecting anomalies: {e}", level="error")
    return anomalies

def clean_data(data: pd.DataFrame, fill_method: str = 'ffill') -> pd.DataFrame:
    """
    Очищает данные, заполняя пропущенные значения и удаляя аномалии.
    :param data: Данные для очистки.
    :param fill_method: Метод заполнения пропущенных значений ('ffill', 'bfill', 'mean').
    :return: Очищенные данные.
    """
    try:
        # Заполнение пропущенных значений
        if fill_method == 'ffill':
            data.fillna(method='ffill', inplace=True)
        elif fill_method == 'bfill':
            data.fillna(method='bfill', inplace=True)
        elif fill_method == 'mean':
            data.fillna(data.mean(), inplace=True)

        # Удаление строк с оставшимися пропущенными значениями
        data.dropna(inplace=True)

        # Удаление аномалий
        anomalies = detect_anomalies(data)
        for column, indices in anomalies.items():
            if indices:
                data.drop(indices, inplace=True)

        log_event("Data Cleaning", "Data cleaning completed successfully.")
        return data
    except Exception as e:
        log_event("Data Cleaning", f"Error cleaning data: {e}", level="error")
        return data