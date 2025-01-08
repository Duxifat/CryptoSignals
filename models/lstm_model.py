import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, Callback
from sklearn.preprocessing import MinMaxScaler
import datetime
import logging
import os
from utils.logging_utils import log_ai_training_progress

class LSTMModel:
    def __init__(self, input_shape, model_path="models/lstm_model.keras"):
        """
        Инициализация LSTM-модели.
        :param input_shape: Форма входных данных (например, (60, 1) для 60 временных шагов и 1 признака).
        :param model_path: Путь для сохранения/загрузки модели.
        """
        self.input_shape = input_shape
        self.model_path = model_path
        self.model = self._build_model()
        self.is_trained = False
        self.last_trained = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def _build_model(self):
        """
        Создает архитектуру LSTM-модели.
        :return: Модель Keras.
        """
        model = Sequential()
        model.add(Input(shape=self.input_shape))
        model.add(LSTM(50, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    @staticmethod
    def prepare_data(data, look_back=60):
        """
        Подготавливает данные для обучения модели.
        :param data: DataFrame с историческими данными.
        :param look_back: Количество временных шагов для анализа.
        :return: X (входные данные), y (целевые значения), scaler (объект для нормализации).
        """
        try:
            if data is None or data.empty:
                raise ValueError("Data is None or empty.")
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(data['close'].values.reshape(-1, 1))
            X, y = [], []
            for i in range(look_back, len(scaled_data)):
                X.append(scaled_data[i - look_back:i, 0])
                y.append(scaled_data[i, 0])
            X, y = np.array(X), np.array(y)
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            return X, y, scaler
        except Exception as e:
            logging.error(f"Error preparing data: {e}")
            raise

    def train(self, X_train, y_train, epochs=50, batch_size=32, validation_split=0.2):
        """
        Обучает модель на предоставленных данных.
        :param X_train: Входные данные для обучения.
        :param y_train: Целевые значения для обучения.
        :param epochs: Количество эпох обучения.
        :param batch_size: Размер батча.
        :param validation_split: Доля данных для валидации.
        """
        try:
            if X_train is None or y_train is None:
                raise ValueError("Training data is None.")
            
            logging.info(f"Starting training for {epochs} epochs.")
            
            # Callbacks для ранней остановки и сохранения лучшей модели
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
                ModelCheckpoint(self.model_path, monitor='val_loss', save_best_only=True),
                TrainingProgressLogger()
            ]
            
            history = self.model.fit(
                X_train, 
                y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                callbacks=callbacks
            )
            
            self.is_trained = True
            self.last_trained = datetime.datetime.now()
            
            logging.info(f"Training completed. Final loss: {history.history['loss'][-1]}")
        except Exception as e:
            logging.error(f"Error during training: {e}")
            raise

    def predict(self, X_test):
        """
        Прогнозирует значения на основе входных данных.
        :param X_test: Входные данные для прогнозирования.
        :return: Прогнозируемые значения.
        """
        try:
            if X_test is None:
                raise ValueError("Test data is None.")
            return self.model.predict(X_test)
        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            raise

    def save_model(self, filepath=None):
        """
        Сохраняет модель в файл.
        :param filepath: Путь для сохранения модели (если None, используется self.model_path).
        """
        try:
            if filepath is None:
                filepath = self.model_path

            # Убедимся, что путь заканчивается на .keras
            if not filepath.endswith('.keras'):
                filepath += '.keras'

            self.model.save(filepath)
            logging.info(f"Model saved to {filepath}.")
        except Exception as e:
            logging.error(f"Error saving model: {e}")
            raise

    def load_model(self, filepath=None):
        """
        Загружает модель из файла.
        :param filepath: Путь к файлу модели (если None, используется self.model_path).
        :return: Загруженная модель.
        """
        try:
            if filepath is None:
                filepath = self.model_path

            # Убедимся, что путь заканчивается на .keras
            if not filepath.endswith('.keras'):
                filepath += '.keras'

            from tensorflow.keras.models import load_model
            self.model = load_model(filepath)
            self.is_trained = True
            logging.info(f"Model loaded from {filepath}.")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise


class TrainingProgressLogger(Callback):
    """
    Callback для логирования прогресса обучения.
    """
    def __init__(self):
        super().__init__()
        self.epoch = 0

    def set_model(self, model):  # <-- ADD
        """
        Явно добавляем метод set_model, чтобы избежать ошибки 'no attribute set_model'
        при вызове Keras в некоторых версиях TF.
        """
        super().set_model(model)

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch = epoch

    def on_epoch_end(self, epoch, logs=None):
        if logs:
            loss = logs.get('loss', 0.0)
            val_loss = logs.get('val_loss', 0.0)
            # Логируем прогресс через нашу функцию из logging_utils
            log_ai_training_progress(epoch + 1, loss, val_loss)
