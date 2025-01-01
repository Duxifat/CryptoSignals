import pandas as pd
import logging

def validate_data(data):
    try:
        if data is None or data.empty:
            logging.warning("Data validation failed: Data is None or empty.")
            return False

        if not isinstance(data, pd.DataFrame):
            logging.warning("Data validation failed: Data is not a pandas DataFrame.")
            return False

        if data.isnull().any().any():
            logging.warning("Data validation failed: Missing values detected.")
            return False

        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logging.warning(f"Data validation failed: Missing required columns. Expected: {required_columns}")
            return False

        logging.info("Data validation successful.")
        return True
    except Exception as e:
        logging.error(f"Error during data validation: {e}")
        return False