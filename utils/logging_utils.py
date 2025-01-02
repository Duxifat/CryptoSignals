import logging
import tkinter as tk
import os

class TextWindowHandler(logging.Handler):
    """Обработчик для вывода логов в текстовое окно."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        """Выводит сообщение в текстовое окно."""
        log_message = self.format(record)
        self.text_widget.insert(tk.END, log_message + "\n")  # Добавляем сообщение в конец окна
        self.text_widget.see(tk.END)  # Прокручиваем окно до последнего сообщения

def setup_logging(log_file="logs/application.log", level=logging.INFO):
    """
    Настройка логирования для записи в файл и вывода в консоль.
    
    :param log_file: Путь к файлу логов (по умолчанию: 'logs/application.log').
    :param level: Уровень логирования (по умолчанию: logging.INFO).
    """
    # Создаем папку logs, если её нет
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Формат логов
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Настройка логирования
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),  # Запись в файл с кодировкой UTF-8
            logging.StreamHandler()                           # Вывод в консоль
        ]
    )
    logging.info("Logging is configured.")

def log_event(event_type, message, level="info"):
    """
    Логирует событие с указанным типом и уровнем.
    
    :param event_type: Тип события (например, "AI Training", "Data Fetching").
    :param message: Сообщение для логирования.
    :param level: Уровень логирования ('info', 'warning', 'error', 'critical').
    """
    log_message = f"[{event_type}] {message}"
    if level == "info":
        logging.info(log_message)
    elif level == "warning":
        logging.warning(log_message)
    elif level == "error":
        logging.error(log_message)
    elif level == "critical":
        logging.critical(log_message)
    else:
        logging.debug(log_message)

def log_ai_training_start():
    """Логирует начало обучения ИИ."""
    log_event("AI Training", "AI training started.")

def log_ai_training_complete(duration=None):
    """Логирует успешное завершение обучения ИИ."""
    message = "AI training completed successfully."
    if duration:
        message += f" Training took {duration} seconds."
    log_event("AI Training", message)

def log_ai_training_error(error):
    """Логирует ошибку при обучении ИИ."""
    log_event("AI Training", f"Error during training: {str(error)}", level="error")

def log_prediction_start():
    """Логирует начало прогнозирования."""
    log_event("Prediction", "Price movement prediction started.")

def log_prediction_result(result):
    """Логирует результат прогнозирования."""
    log_event("Prediction", f"Prediction result: {result}")

def log_prediction_error(error):
    """Логирует ошибку при прогнозировании."""
    log_event("Prediction", f"Error during prediction: {str(error)}", level="error")

def log_data_fetching(symbol, timeframe):
    """Логирует успешное получение данных."""
    log_event("Data Fetching", f"Historical data for {symbol} ({timeframe}) fetched successfully.")

def log_data_fetching_error(symbol, timeframe, error):
    """Логирует ошибку при получении данных."""
    log_event("Data Fetching", f"Error fetching data for {symbol} ({timeframe}): {str(error)}", level="error")

def log_data_validation(success=True):
    """Логирует результат валидации данных."""
    if success:
        log_event("Data Validation", "Data validation successful.")
    else:
        log_event("Data Validation", "Data validation failed.", level="warning")

def log_user_action(action):
    """Логирует действия пользователя."""
    log_event("User Action", f"User clicked '{action}'.")

def log_critical_error(error):
    """Логирует критические ошибки."""
    log_event("Critical Error", f"Critical error: {str(error)}", level="critical")

def log_analysis_step(step, message):
    """Логирует шаг анализа."""
    log_event("Analysis", f"Step {step}: {message}")

def log_application_start():
    """Логирует запуск приложения."""
    log_event("Application", "Application started.")

def log_application_stop():
    """Логирует завершение работы приложения."""
    log_event("Application", "Application stopped.")