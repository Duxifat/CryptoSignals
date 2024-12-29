import numpy as np
import logging
from models.smart_ai_model import SmartAIModel  # Импорт умной модели

class AIPredictor:
    def __init__(self, smart_model_path="models/smart_ai_model.h5"):
        """
        Initialize AI Predictor with Smart AI Model.
        """
        try:
            self.smart_model = SmartAIModel(input_shape=(60, 4), lstm_model_path=smart_model_path)
            logging.info("Smart AI Model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading Smart AI Model: {e}")
            self.smart_model = None

    def preprocess_data(self, data):
        """
        Normalize and clean data for AI analysis.
        :param data: DataFrame with historical price data
        :return: Normalized DataFrame
        """
        try:
            normalized_data = (data - data.mean()) / data.std()
            logging.info("Data preprocessed successfully for AI analysis.")
            return normalized_data
        except Exception as e:
            logging.error(f"Error in data preprocessing: {e}")
            return data

    def predict_price_movement(self, data):
        """
        Predict if price will move up, down, or remain neutral using Smart AI Model.
        :param data: DataFrame with historical price data
        :return: 'up', 'down', or 'neutral'
        """
        if self.smart_model is None:
            logging.error("Smart AI Model not loaded.")
            return 'neutral'

        try:
            X, _ = self.smart_model.preprocess_data(data, look_back=60)
            predictions = self.smart_model.predict(X)

            # Use the last prediction to decide
            last_prediction = predictions[-1]
            last_close = data['close'].iloc[-1]

            logging.info(f"Prediction: {last_prediction}, Last Close: {last_close}")

            return 'up' if last_prediction > last_close else 'down'
        except Exception as e:
            logging.error(f"Error in Smart AI prediction: {e}")
            return 'neutral'

    def classify_market(self, data):
        """
        Classify the market as trending or ranging.
        :param data: DataFrame with historical price data
        :return: 'trend', 'range', or 'unknown'
        """
        try:
            rolling_std = data['close'].rolling(window=20).std()
            if rolling_std.mean() > 0.01:
                return "trend"
            else:
                return "range"
        except Exception as e:
            logging.error(f"Error in market classification: {e}")
            return "unknown"

    def smart_analysis(self, data):
        """
        Analyze market trends using Smart AI Model.
        :param data: DataFrame with historical price data
        :return: 'up', 'down', or 'neutral'
        """
        try:
            return self.predict_price_movement(data)
        except Exception as e:
            logging.error(f"Error in Smart Analysis: {e}")
            return 'neutral'
