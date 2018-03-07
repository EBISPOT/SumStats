from sumstats.server.app import app

import logging
import logging.config
import cherrypy
from paste.translogger import TransLogger
from sumstats.server import api_utils as apiu
from sumstats.server.api_utils import properties


LOG_CONF = {
    'version': 1,

    'formatters': {
        'void': {
            'format': ''
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'cherrypy_console': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'void',
            'stream': 'ext://sys.stdout'
        },
        'cherrypy_access': {
            'level':'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'void',
            'filename': 'access.log',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
        'cherrypy_error': {
            'level':'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'void',
            'filename': 'errors.log',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO'
        },
        'wsgi': {
            'handlers': ['cherrypy_access'],
            'level': 'INFO' ,
            'propagate': False
        },
        'cherrypy.access': {
            'handlers': ['cherrypy_access'],
            'level': 'INFO',
            'propagate': False
        },
        'cherrypy.error': {
            'handlers': ['cherrypy_console', 'cherrypy_error'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

logger = logging.getLogger()


def main():
    apiu._set_properties()
    # Enable WSGI access logging via Paste
    app_logged = TransLogger(app, setup_console_handler=False)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, "/")
    access_log = LOG_CONF['handlers']['cherrypy_access']['filename']
    LOG_CONF['handlers']['cherrypy_access']['filename'] = properties.logging_path + "/" + access_log
    error_log = LOG_CONF['handlers']['cherrypy_error']['filename']
    LOG_CONF['handlers']['cherrypy_error']['filename'] = properties.logging_path + "/" + error_log
    
    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload_on': True,
        'log.screen': True,
        'server.socket_port': 8080,
        'server.socket_host': '0.0.0.0',
        'server.socket_pool': 30,
    })

    logging.config.dictConfig(LOG_CONF)

    # Unsuscribe the default server
    cherrypy.server.unsubscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    # Subscribe this server
    server.subscribe()

    # Start the server engine (Option 1 *and* 2)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()
