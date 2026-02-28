import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "tradebot.log")
MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3

_configured = False


def setupLogging() -> logging.Logger:
    global _configured
    logger = logging.getLogger("tradebot")

    if _configured:
        return logger

    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleFmt = logging.Formatter("%(levelname)-8s │ %(message)s")
    consoleHandler.setFormatter(consoleFmt)

    os.makedirs(LOG_DIR, exist_ok=True)
    fileHandler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    fileHandler.setLevel(logging.DEBUG)
    fileFmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fileHandler.setFormatter(fileFmt)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    _configured = True
    return logger
