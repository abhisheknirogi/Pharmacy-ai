"""Logging configuration for the application."""
import logging
import logging.handlers
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "../../logs")
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging(name: str, level=logging.INFO):
    """Setup logging for a module."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler (force UTF-8 where supported to avoid encoding errors)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    try:
        # reconfigure stream encoding if available (Python 3.7+)
        console_handler.stream.reconfigure(encoding='utf-8')
    except Exception:
        pass
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # File handler
    log_file = os.path.join(LOG_DIR, f"pharmarec_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Setup root logger
app_logger = setup_logging("pharmarec", logging.INFO)
