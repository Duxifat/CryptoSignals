import numpy as np
import pandas as pd
import json
import os
import time
import datetime
import logging
import asyncio
from models.lstm_model import LSTMModel
from data_fetcher import DataFetcher
from utils.logging_utils import (
    log_ai_training_start,
    log_ai_training_complete,
    log_ai_training_error,
    log_prediction_start,
    log_prediction_result,
    log_prediction_error,
    log_event
)

class AIPredictor:
    def __init__(self):
        """
        Инициализация AIPredictor.
        """
        self.models = {}  # Словарь для хранения моделей, обученных на разных таймфреймах
        self.timeframes = {
            "short_term": ["1", "3", "5", "15", "30", "60"],  # 1мин, 3мин, 5мин, 15мин, 30мин, 1час
            "medium_term": ["60", "240", "D"]  # 1час, 4часа, 1день
        }
        self.state_file = "ai_state.json"
        self.last_trained = self._load_state()
        self.fetcher = DataFetcher()

    def _load_state(self):
        """
        Загружает состояние модели из файла.
        :return: Время последнего обучения или None, если файл не существует.
        """
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
                return datetime.datetime.fromisoformat(state["last_trained"])
        return None

    def _save_state(self):
        """
        Сохраняет состояние модели в файл.
        """
        state = {
            "last_trained": self.last_trained.isoformat() if self.last_trained else None
        }
        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f)
        except Exception as e:
            log_ai_training_error(f"Error saving AI state: {e}")

    def get_ai_status(self):
        """
        Возвращает статус ИИ и время последнего обучения.
        :return: Кортеж (статус, время последнего обучения).
        """
        status = "Обучена" if self.last_trained else "Не обучена"
        if self.last_trained:
            formatted_time = self.last_trained.strftime("%d-%m-%Y %H:%M:%S")
            return status, formatted_time
        return status, None

    def get_training_recommendation(self):
        """
        Рекомендует обучение, если прошло больше 7 дней с последнего обучения.
        :return: Рекомендация в виде строки.
        """
        if not self.last_trained:
            return "Обучить ИИ"
        days_since_training = (datetime.datetime.now() - self.last_trained).days
        if days_since_training > 7:
            return f"Обучить ИИ (прошло {days_since_training} дней)"
        next_training_date = self.last_trained + datetime.timedelta(days=7)
        formatted_date = next_training_date.strftime("%d-%m-%Y %H:%M:%S")
        return f"Обучить ИИ снова после {formatted_date}"

    async def train_ai_on_all_timeframes(self, symbols):
        """
        Обучает ИИ на всех таймфреймах для всех пар.
        :param symbols: Список торговых пар.
        """
        log_ai_training_start()
        try:
            for timeframe_type, timeframes in self.timeframes.items():
                for timeframe in timeframes:
                    model_key = f"{timeframe_type}_{timeframe}"
                    self.models[model_key] = LSTMModel(input_shape=(60, 1))
                    await self._train_ai_on_timeframe(symbols, timeframe, model_key)
            self.last_trained = datetime.datetime.now()
            self._save_state()
            log_ai_training_complete()
        except Exception as e:
            log_ai_training_error(f"Error during training: {e}")
            raise

    async def _train_ai_on_timeframe(self, symbols, timeframe, model_key):
        """
        Обучает ИИ на данных для конкретного таймфрейма.
        :param symbols: Список торговых пар.
        :param timeframe: Таймфрейм.
        :param model_key: Ключ модели.
        """
        log_event("AI Training", f"Starting training for timeframe: {timeframe}")
        try:
            all_data = []
            tasks = [self.fetcher.fetch_historical_data_async(symbol, timeframe) for symbol in symbols]
            results = await asyncio.gather(*tasks)
            for data in results:
                if not data.empty:
                    all_data.append(data)

            if not all_data:
                raise ValueError("No data fetched for any symbol.")
            combined_data = pd.concat(all_data)
            X, y, scaler = LSTMModel.prepare_data(combined_data)
            self.models[model_key].train(X, y)
            log_event("AI Training", f"Training completed for timeframe: {timeframe}")
        except Exception as e:
            log_event("AI Training", f"Error during training for timeframe {timeframe}: {e}", level="error")
            raise

    def predict_price_movement(self, data, timeframe_type="short_term"):
        """
        Прогнозирует движение цены для конкретного таймфрейма.
        :param data: Данные для прогнозирования.
        :param timeframe_type: Тип таймфрейма (short_term или medium_term).
        :return: Словарь с прогнозами для каждого таймфрейма.
        """
        log_prediction_start()
        try:
            if data is None or data.empty:
                raise ValueError("No data provided for prediction.")
            predictions = {}
            for timeframe in self.timeframes[timeframe_type]:
                model_key = f"{timeframe_type}_{timeframe}"
                if model_key in self.models:
                    X, y, scaler = LSTMModel.prepare_data(data)
                    prediction = self.models[model_key].predict(X)
                    predictions[timeframe] = prediction[-1]
            log_prediction_result(predictions)
            return predictions
        except Exception as e:
            log_prediction_error(f"Error during prediction: {e}")
            raise