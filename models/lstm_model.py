import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

class LSTMModel:
    def __init__(self, input_shape):
        self.input_shape = input_shape
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=self.input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    @staticmethod
    def prepare_data(data, look_back=60):
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data['close'].values.reshape(-1, 1))

        X, y = [], []
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i-look_back:i, 0])
            y.append(scaled_data[i, 0])

        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        return X, y, scaler

    def train(self, X_train, y_train, epochs=50, batch_size=32):
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2)

    def predict(self, X_test):
        return self.model.predict(X_test)

    def save_model(self, file_path):
        self.model.save(file_path)

    @staticmethod
    def load_model(file_path):
        from tensorflow.keras.models import load_model
        return load_model(file_path)