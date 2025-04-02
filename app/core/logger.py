import logging
from app.core.config import Logs
from app.core.config import settings



def get_logger(name: str, logger_level: str = settings.LOG_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(Logs.LOG_LEVELS.get(logger_level))
    logger.propagate = False
    if not logger.handlers:
        ch = config_handler(logger_level)
        logger.addHandler(ch)
    return logger

def config_handler(logger_level: str = settings.LOG_LEVEL):
    ch = logging.StreamHandler()
    ch.setLevel(Logs.LOG_LEVELS.get(logger_level))
    formatter = logging.Formatter(Logs.LOG_FORMAT)
    ch.setFormatter(formatter)
    return ch

