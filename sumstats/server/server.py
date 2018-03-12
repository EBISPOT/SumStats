from sumstats.server.app import app

import logging
import logging.config
import cherrypy
from paste.translogger import TransLogger
import sumstats.server.api_utils as apiu

logger = logging.getLogger()


def main():
    # Enable WSGI access logging via Paste
    app_logged = TransLogger(app, setup_console_handler=False)

    # Set properties
    apiu._set_properties()
    LOG_CONF = apiu.properties.LOG_CONF

    LOG_LEVEL = apiu.properties.LOG_LEVEL
    print("Setting to logging level:", LOG_LEVEL)
    LOG_CONF = _set_log_level(LOG_CONF=LOG_CONF, LOG_LEVEL=LOG_LEVEL)
    LOG_CONF = _set_log_path(LOG_CONF=LOG_CONF, loggin_path=apiu.properties.logging_path)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, "/")

    # Set logging configuration
    logging.config.dictConfig(LOG_CONF)

    # Unsuscribe the default server
    cherrypy.server.unsubscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    # Set the configuration of the web server
    server.socket_host = "0.0.0.0"
    server.socket_port = 8080
    server.socket_pool = 30

    # Subscribe this server
    server.subscribe()

    # Start the server engine (Option 1 *and* 2)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()


def _set_log_level(LOG_CONF, LOG_LEVEL):
    for handler in LOG_CONF['handlers']:
        LOG_CONF['handlers'][handler]['level'] = LOG_LEVEL
    for loggr in LOG_CONF['loggers']:
        LOG_CONF['loggers'][loggr]['level'] = LOG_LEVEL
    return LOG_CONF


def _set_log_path(LOG_CONF, loggin_path):
    access_log = LOG_CONF['handlers']['cherrypy_access']['filename']
    LOG_CONF['handlers']['cherrypy_access']['filename'] = loggin_path + "/" + access_log
    error_log = LOG_CONF['handlers']['cherrypy_error']['filename']
    LOG_CONF['handlers']['cherrypy_error']['filename'] = loggin_path + "/" + error_log
    logger_log = LOG_CONF['handlers']['logger']['filename']
    LOG_CONF['handlers']['logger']['filename'] = loggin_path + "/" + logger_log
    return LOG_CONF