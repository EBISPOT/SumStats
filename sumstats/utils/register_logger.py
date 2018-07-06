from config import properties
import logging
from logging import config
from sumstats.utils import properties_handler as set_p


def register(logger_name):
    set_p.set_properties()

    properties.LOG_CONF['loggers'][logger_name] = {
        'handlers': ['logger'],
        'propagate': False
    }
    LOG_CONF = set_log_path(properties)
    logging.config.dictConfig(LOG_CONF)


def set_log_path(properties):
    properties.LOG_CONF['handlers'][properties.LOGGER_HANDLER]['filename'] = properties.logging_path + "/" + properties.LOGGER_LOG
    return properties.LOG_CONF