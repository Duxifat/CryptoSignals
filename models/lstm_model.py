import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from sklearn.preprocessing import MinMaxScaler
import datetime
import logging

class LSTMModel:
    def __init__(self, input_shape):
        self.input_shape = input_shape
        self.model = self._build_model()
        self.is_trained = False
        self.last_trained = None

    def _build_model(self):
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
        try:
            if data is None or data.empty:
                raise ValueError("Data is None or empty.")
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(data['close'].values.reshape(-1, 1))
            X, y = [], []
            for i in range(look_back, len(scaled_data)):
                X.append(scaled_data[i-look_back:i, 0])
                y.append(scaled_data[i, 0])
            X, y = np.array(X), np.array(y)
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            return X, y, scaler
        except Exception as e:
            logging.error(f"Error preparing data: {e}")
            raise

    def train(self, X_train, y_train, epochs=50, batch_size=32):
        try:
            if X_train is None or y_train is None:
                raise ValueError("Training data is None.")
            self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2)
            self.is_trained = True
            self.last_trained = datetime.datetime.now()
        except Exception as e:
            logging.error(f"Error during training: {e}")
            raise

    def predict(self, X_test):
        try:
            if X_test is None:
                raise ValueError("Test data is None.")
            return self.model.predict(X_test)
        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            raise