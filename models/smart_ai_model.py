import numpy as np
import pandas as pd
import logging
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import ta  # Для расчёта индикаторов

class SmartAIModel:
    def __init__(self, input_shape, lstm_model_path=None):
        self.input_shape = input_shape
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = self._build_model()
        if lstm_model_path:
            self.load_model(lstm_model_path)

    def _build_model(self):
        """
        Построение архитектуры LSTM.
        """
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=self.input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def preprocess_data(self, data, look_back=60):
        """
        Подготовка данных для LSTM, включая нормализацию и добавление индикаторов.
        """
        # Добавляем индикаторы
        data['rsi'] = ta.momentum.RSIIndicator(data['close'], window=14).rsi()
        data['ema_20'] = ta.trend.EMAIndicator(data['close'], window=20).ema_indicator()
        data['ema_50'] = ta.trend.EMAIndicator(data['close'], window=50).ema_indicator()

        # Нормализация
        scaled_data = self.scaler.fit_transform(data[['close', 'rsi', 'ema_20', 'ema_50']].fillna(0))
        
        # Формирование временных рядов
        X, y = [], []
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i-look_back:i])
            y.append(scaled_data[i, 0])  # Предсказываем 'close'
        
        return np.array(X), np.array(y)

    def train(self, X_train, y_train, epochs=50, batch_size=32):
        """
        Обучение модели.
        """
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2)

    def predict(self, X_test):
        """
        Предсказание на тестовых данных.
        """
        predictions = self.model.predict(X_test)
        return self.scaler.inverse_transform(np.concatenate([predictions, np.zeros((predictions.shape[0], 3))], axis=1))[:, 0]

    def save_model(self, file_path):
        """
        Сохранение модели.
        """
        self.model.save(file_path)

    def load_model(self, file_path):
        """
        Загрузка модели.
        """
        from tensorflow.keras.models import load_model
        self.model = load_model(file_path)
