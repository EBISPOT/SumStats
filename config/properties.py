h5files_path="./files/output"
tsvfiles_path="./files/toload"
bp_step=16
max_bp=300000000
snp_dir="bysnp"
chr_dir="bychr"
trait_dir="bytrait"
ols_terms_location= "https://www.ebi.ac.uk/ols/api/terms?id="
gwas_study_location="http://wwwdev.ebi.ac.uk/gwas/beta/rest/api/studies/"
logging_path="./logs"
port=8080
APPLICATION_ROOT="/gwas/summary-statistics/api"
LOG_LEVEL="INFO"
ACCESS_LOG="access.log"
ERROR_LOG="error.log"
LOGGER_LOG="logger.log"
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
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'cherrypy_access': {
            'level':'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
        'cherrypy_error': {
            'level':'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
        'logger': {
            'level':'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        '': {
            'handlers': ['logger'],
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