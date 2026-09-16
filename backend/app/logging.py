"""Structured application logging."""

import logging
import sys
from backend.app.config import get_settings


def setup_logging():
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True
    )

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def mask_sensitive_data(value: str) -> str:
    """Mask document or personal identifiers for privacy/security logs."""
    if not value or len(value) < 4:
        return "***"
    return f"{value[:2]}***{value[-2:]}"
