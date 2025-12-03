import logging
import json
from logging.handlers import RotatingFileHandler
from app.core.config import settings


class RequestIDFilter(logging.Filter):
    """
    Inject request_id into every log record.
    """
    def filter(self, record):
        record.request_id = getattr(record, "request_id", "-")
        return True


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logs.
    """
    def format(self, record):
        log = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        return json.dumps(log)


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL.upper())

    # Remove duplicate handlers on reload
    for h in list(logger.handlers):
        logger.removeHandler(h)

    request_filter = RequestIDFilter()

    # Console Handler
    console = logging.StreamHandler()
    console.setLevel(settings.LOG_LEVEL.upper())
    console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s"
    ))
    console.addFilter(request_filter)
    logger.addHandler(console)

    # Text log
    if settings.LOG_FILE:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10_000_000,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(settings.LOG_LEVEL.upper())
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s"
        ))
        file_handler.addFilter(request_filter)
        logger.addHandler(file_handler)

    # JSON Log
    if getattr(settings, "JSON_LOG_FILE", None):
        json_handler = RotatingFileHandler(
            settings.JSON_LOG_FILE,
            maxBytes=10_000_000,
            backupCount=5,
            encoding="utf-8"
        )
        json_handler.setLevel(settings.LOG_LEVEL.upper())
        json_handler.setFormatter(JSONFormatter())
        json_handler.addFilter(request_filter)
        logger.addHandler(json_handler)

    return logger


logger = configure_logging()
