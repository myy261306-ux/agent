"""
Logging Configuration Module
Centralized logging setup for the agent system
"""

import logging
import logging.handlers
from pathlib import Path
from utils.config import Config


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Setup and return a configured logger instance

    Args:
        name: Logger name (usually __name__)
        log_file: Optional file path for logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.hasHandlers():
        return logger

    logger.setLevel(Config.LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(Config.LOG_LEVEL)

    # Formatter
    if Config.ENABLE_VERBOSE_MODE:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        )
    else:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if log_file specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB per file
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create main system logger
system_logger = setup_logger("AgentSystem")
