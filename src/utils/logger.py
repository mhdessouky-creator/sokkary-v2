"""
Logging configuration for Sokkary V2
"""

import sys
from pathlib import Path
from loguru import logger
from src.config.settings import settings


def setup_logger():
    """
    Configure the application logger
    """
    # Remove default handler
    logger.remove()

    # Console handler with custom format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
    )

    # File handler
    log_file = settings.log_dir / "sokkary-v2.log"
    logger.add(
        log_file,
        format=log_format,
        level=settings.log_level,
        rotation="100 MB",
        retention=f"{settings.log_retention_days} days",
        compression="zip",
    )

    if settings.debug:
        logger.debug("Debug mode enabled")

    logger.info("Logger initialized")
    return logger


def get_logger(name: str = __name__):
    """
    Get a logger instance with the specified name

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)


# Initialize logger on import
setup_logger()
