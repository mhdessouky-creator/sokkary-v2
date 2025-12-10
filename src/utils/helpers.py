"""
Helper utilities for Sokkary V2
"""

import time
import json
from typing import Any, Dict
from functools import wraps
from src.utils.logger import get_logger

logger = get_logger(__name__)


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        user_input: Raw user input

    Returns:
        Sanitized input
    """
    if not isinstance(user_input, str):
        return str(user_input)

    # Remove potential command injection patterns
    dangerous_patterns = [
        ";", "&&", "||", "|", ">", "<",
        "$(", "`", "\n", "\r"
    ]

    sanitized = user_input
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, "")

    return sanitized.strip()


def format_response(response: Dict[str, Any]) -> str:
    """
    Format a response dictionary into a readable string

    Args:
        response: Response dictionary

    Returns:
        Formatted string
    """
    try:
        return json.dumps(response, indent=2, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.error(f"Error formatting response: {e}")
        return str(response)


def measure_time(func):
    """
    Decorator to measure function execution time

    Args:
        func: Function to measure

    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time

        logger.debug(
            f"Function '{func.__name__}' executed in {duration:.4f} seconds"
        )

        return result

    return wrapper


def validate_dict_structure(data: Dict, required_keys: list[str]) -> bool:
    """
    Validate that a dictionary has required keys

    Args:
        data: Dictionary to validate
        required_keys: List of required keys

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False

    return all(key in data for key in required_keys)


def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with a default

    Args:
        data: Dictionary to get value from
        key: Key to look up
        default: Default value if key not found

    Returns:
        Value or default
    """
    try:
        return data.get(key, default)
    except (AttributeError, TypeError):
        return default


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
