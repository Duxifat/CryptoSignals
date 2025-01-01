import numpy as np
import pandas as pd
import logging
from models.lstm_model import LSTMModel

class AIPredictor:
    def __init__(self):
        self.model = LSTMModel(input_shape=(60, 1))
        logging.info("AI Predictor initialized successfully.")

    def predict_price_movement(self, data):
        try:
            X, y, scaler = LSTMModel.prepare_data(data)
            predictions = self.model.predict(X)
            return predictions
        except Exception as e:
            logging.error(f"Error predicting price movement: {e}")
            return None