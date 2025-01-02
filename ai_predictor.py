import numpy as np
import pandas as pd
import json
import os
import time
import datetime
from models.lstm_model import LSTMModel
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
        self.last_trained = self._load_state()  # Загружаем состояние при инициализации

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
        return status, self.last_trained

    def get_training_recommendation(self):
        """Рекомендует обучение, если прошло больше 7 дней с последнего обучения."""
        if not self.last_trained:
            return "Обучить ИИ"
        days_since_training = (datetime.datetime.now() - self.last_trained).days
        if days_since_training > 7:
            return f"Обучить ИИ (прошло {days_since_training} дней)"
        return "Обучение не требуется"

    def train_ai(self, data):
        """Запускает обучение ИИ."""
        log_ai_training_start()
        try:
            start_time = time.time()
            X, y, scaler = LSTMModel.prepare_data(data)
            self.model.train(X, y)
            self.last_trained = datetime.datetime.now()
            self._save_state()  # Сохраняем состояние после обучения
            training_time = time.time() - start_time
            log_ai_training_complete(training_time)
        except Exception as e:
            log_ai_training_error(e)
            raise

    def predict_price_movement(self, data):
        """Прогнозирует движение цены."""
        log_prediction_start()
        try:
            X, y, scaler = LSTMModel.prepare_data(data)
            predictions = self.model.predict(X)
            log_prediction_result(predictions[-1])
            return predictions
        except Exception as e:
            log_prediction_error(e)
            return None