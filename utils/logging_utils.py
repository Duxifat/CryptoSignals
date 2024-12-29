
import logging

def setup_logging(log_file="application.log", level=logging.INFO):
    """Set up logging to a file and the console."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging is configured.")
