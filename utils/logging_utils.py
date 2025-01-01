import logging
import os

def setup_logging(log_file="logs/application.log", level=logging.INFO):
    # Создаем папку logs, если её нет
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Настройка логирования
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging is configured.")