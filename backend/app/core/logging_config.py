import logging
from logging.config import dictConfig

from app.core.config import get_settings


def setup_logging() -> None:
    """
    Configure application-wide logging.
    Uses standard logging with a clear, production-friendly format.
    """

    settings = get_settings()

    log_level = "DEBUG" if settings.debug else "INFO"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": (
                    "[%(asctime)s] "
                    "[%(levelname)s] "
                    "[%(name)s] "
                    "%(message)s"
                ),
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": log_level,
            },
        },
        "root": {
            "handlers": ["default"],
            "level": log_level,
        },
    }

    dictConfig(logging_config)
