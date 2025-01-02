import numpy as np
import pandas as pd
import json
import os
import time
import datetime
from models.lstm_model import LSTMModel
from data_fetcher import DataFetcher
from utils.logging_utils import (
    log_ai_training_start,
    log_ai_training_complete,
    log_ai_training_error,
    log_prediction_start,
    log_prediction_result,
    log_prediction_error
)

class AIPredictor:
    def __init__(self):
        self.model = LSTMModel(input_shape=(60, 1))
        self.state_file = "ai_state.json"
        self.last_trained = self._load_state()

    def _load_state(self):
        """Загружает состояние модели из файла."""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
                return datetime.datetime.fromisoformat(state["last_trained"])
        return None

    def _save_state(self):
        """Сохраняет состояние модели в файл."""
        state = {
            "last_trained": self.last_trained.isoformat() if self.last_trained else None
        }
        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f)
        except Exception as e:
            log_ai_training_error(f"Error saving AI state: {e}")

    def get_ai_status(self):
        """Возвращает статус ИИ и время последнего обучения."""
        status = "Обучена" if self.last_trained else "Не обучена"
        if self.last_trained:
            formatted_time = self.last_trained.strftime("%d:%m:%Y %H:%M:%S")
            return status, formatted_time
        return status, None

    def get_training_recommendation(self):
        """Рекомендует обучение, если прошло больше 7 дней с последнего обучения."""
        if not self.last_trained:
            return "Обучить ИИ"
        days_since_training = (datetime.datetime.now() - self.last_trained).days
        if days_since_training > 7:
            return f"Обучить ИИ (прошло {days_since_training} дней)"
        next_training_date = self.last_trained + datetime.timedelta(days=7)
        formatted_date = next_training_date.strftime("%d:%m:%Y %H:%M:%S")
        return f"Обучить ИИ снова после {formatted_date}"

    def train_ai_on_all_pairs(self, symbols):
        """Обучает ИИ на данных всех пар."""
        log_ai_training_start()
        try:
            if not symbols:
                raise ValueError("No symbols provided for training.")
            start_time = time.time()
            all_data = []
            fetcher = DataFetcher()
            for symbol in symbols:
                data = fetcher.fetch_historical_data(symbol, timeframe='1h', limit=200)
                if not data.empty:
                    all_data.append(data)
            if not all_data:
                raise ValueError("No data fetched for any symbol.")
            combined_data = pd.concat(all_data)
            X, y, scaler = LSTMModel.prepare_data(combined_data)
            self.model.train(X, y)
            self.last_trained = datetime.datetime.now()
            self._save_state()
            training_time = time.time() - start_time
            log_ai_training_complete(training_time)
        except ValueError as e:
            log_ai_training_error(f"Validation error: {e}")
            raise
        except Exception as e:
            log_ai_training_error(f"Error during training: {e}")
            raise

    def predict_price_movement(self, data):
        """Прогнозирует движение цены."""
        log_prediction_start()
        try:
            if data is None or data.empty:
                raise ValueError("No data provided for prediction.")
            X, y, scaler = LSTMModel.prepare_data(data)
            predictions = self.model.predict(X)
            log_prediction_result(predictions[-1])
            return predictions
        except ValueError as e:
            log_prediction_error(f"Validation error: {e}")
            raise
        except Exception as e:
            log_prediction_error(f"Error during prediction: {e}")
            raise