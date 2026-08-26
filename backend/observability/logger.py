import logging

from backend import config

_logger = logging.getLogger("cortexrag")

if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    _logger.addHandler(handler)


def log_event(message: str):
    _logger.info(message)
