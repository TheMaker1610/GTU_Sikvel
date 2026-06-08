"""
Централизованный модуль логирования.
Логи пишутся одновременно в консоль и файл logs/gtu.log.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "gtu.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

os.makedirs(LOG_DIR, exist_ok=True)

_configured = False


def _configure_root():
    global _configured
    if _configured:
        return
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    root.addHandler(console)
    root.addHandler(file_handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure_root()
    return logging.getLogger(name)
