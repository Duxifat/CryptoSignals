import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, List
import tkinter as tk

class TextWindowHandler(logging.Handler):
    """Обработчик для вывода логов в текстовое окно."""
    def __init__(self, text_widget: tk.Text):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        """Выводит сообщение в текстовое окно."""
        try:
            log_message = self.format(record)
            self.text_widget.insert(tk.END, log_message + "\n")  # Добавляем сообщение в конец окна
            self.text_widget.see(tk.END)  # Прокручиваем окно до последнего сообщения
        except Exception as e:
            print(f"Error emitting log to text window: {e}")

def setup_logging(log_file: str = "logs/application.log", level: int = logging.INFO, max_log_size: int = 10 * 1024 * 1024, backup_count: int = 5) -> None:
    """
    Настройка логирования для записи в файл и вывода в консоль.
    :param log_file: Путь к файлу логов (по умолчанию: 'logs/application.log').
    :param level: Уровень логирования (по умолчанию: logging.INFO).
    :param max_log_size: Максимальный размер файла лога в байтах (по умолчанию: 10 МБ).
    :param backup_count: Количество резервных копий логов (по умолчанию: 5).
    """
    try:
        # Создаем папку logs, если её нет
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Формат логов
        log_format = "%(asctime)s - %(levelname)s - %(message)s"

        # Настройка ротации логов
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_log_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(log_format))

        # Настройка вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))

        # Настройка основного логгера
        logging.basicConfig(
            level=level,
            handlers=[file_handler, console_handler]
        )

        logging.info("Logging is configured.")
    except Exception as e:
        print(f"Error setting up logging: {e}")

def log_event(event_type: str, message: str, level: str = "info") -> None:
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

def log_ai_training_start() -> None:
    """Логирует начало обучения ИИ."""
    log_event("AI Training", "AI training started.")

def log_ai_training_progress(epoch: int, loss: float, val_loss: float) -> None:
    """Логирует прогресс обучения модели."""
    log_message = f"Epoch {epoch} - Loss: {loss:.4f}, Val Loss: {val_loss:.4f}"
    log_event("AI Training", log_message)

def log_ai_training_complete(duration: Optional[float] = None) -> None:
    """Логирует успешное завершение обучения ИИ."""
    message = "AI training completed successfully."
    if duration:
        message += f" Training took {duration:.2f} seconds."
    log_event("AI Training", message)

def log_ai_training_error(error: Exception) -> None:
    """Логирует ошибку при обучении ИИ."""
    log_event("AI Training", f"Error during training: {str(error)}", level="error")

def log_prediction_start() -> None:
    """Логирует начало прогнозирования."""
    log_event("Prediction", "Price movement prediction started.")

def log_prediction_result(result: Dict[str, float]) -> None:
    """Логирует результат прогнозирования."""
    log_event("Prediction", f"Prediction result: {result}")

def log_prediction_error(error: Exception) -> None:
    """Логирует ошибку при прогнозировании."""
    log_event("Prediction", f"Error during prediction: {str(error)}", level="error")

def log_data_fetching(symbol: str, timeframe: str) -> None:
    """Логирует успешное получение данных."""
    log_event("Data Fetching", f"Historical data for {symbol} ({timeframe}) fetched successfully.")

def log_data_fetching_error(symbol: str, timeframe: str, error: Exception) -> None:
    """Логирует ошибку при получении данных."""
    log_event("Data Fetching", f"Error fetching data for {symbol} ({timeframe}): {str(error)}", level="error")

def log_data_validation(success: bool = True) -> None:
    """Логирует результат валидации данных."""
    if success:
        log_event("Data Validation", "Data validation successful.")
    else:
        log_event("Data Validation", "Data validation failed.", level="warning")

def log_user_action(action: str) -> None:
    """Логирует действия пользователя."""
    log_event("User Action", f"User clicked '{action}'.")

def log_critical_error(error: Exception) -> None:
    """Логирует критические ошибки."""
    log_event("Critical Error", f"Critical error: {str(error)}", level="critical")

def log_analysis_step(step: int, message: str) -> None:
    """Логирует шаг анализа."""
    log_event("Analysis", f"Step {step}: {message}")

def log_application_start() -> None:
    """Логирует запуск приложения."""
    log_event("Application", "Application started.")

def log_application_stop() -> None:
    """Логирует завершение работы приложения."""
    log_event("Application", "Application stopped.")