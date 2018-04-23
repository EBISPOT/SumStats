from config import properties
import logging
from logging import config
from sumstats.utils import properties_handler as set_p


def register(logger_name):
    set_p.set_properties()
    LOG_CONF = properties.LOG_CONF
    LOG_CONF['loggers'][logger_name] = {
        'handlers': ['logger'],
        'propagate': False
    }
    properties.LOG_CONF['handlers']['cherrypy_access'][
        'filename'] = properties.logging_path + "/" + properties.ACCESS_LOG
    properties.LOG_CONF['handlers']['cherrypy_error']['filename'] = properties.logging_path + "/" + properties.ERROR_LOG
    properties.LOG_CONF['handlers']['logger']['filename'] = properties.logging_path + "/" + properties.LOGGER_LOG
    logging.config.dictConfig(LOG_CONF)