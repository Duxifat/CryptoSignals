import pandas as pd
import logging

def validate_data(data):
    """Validate the integrity of a data frame."""
    try:
        # Проверка на None или пустые данные
        if data is None or data.empty:
            logging.warning("Data validation failed: Data is None or empty.")
            return False

        # Проверка типа данных
        if not isinstance(data, pd.DataFrame):
            logging.warning("Data validation failed: Data is not a pandas DataFrame.")
            return False

        # Проверка на наличие пропущенных значений
        if data.isnull().any().any():
            logging.warning("Data validation failed: Missing values detected.")
            return False

        # Проверка на наличие обязательных колонок
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logging.warning(f"Data validation failed: Missing required columns. Expected: {required_columns}")
            return False

        logging.info("Data validation successful.")
        return True
    except Exception as e:
        logging.error(f"Error during data validation: {e}")
        return False
