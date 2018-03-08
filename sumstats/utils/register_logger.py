from config import properties
import logging
from logging import config


def register(logger_name):
    LOG_CONF = properties.LOG_CONF
    LOG_CONF['loggers'][logger_name] = {
        'handlers': ['logger'],
        'propagate': False
    }
    logging.config.dictConfig(LOG_CONF)