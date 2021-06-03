h5files_path="./files/output"
tsvfiles_path="./files/toload"
loaded_files_path="./files/loaded"
bp_step=16
available_chromosomes=24
max_bp=300000000
snp_dir="bysnp"
study_dir="bystudy"
chr_dir="bychr"
trait_dir="bytrait"
ols_terms_location= "https://www.ebi.ac.uk/ols/api/terms?id="
gwas_study_location="http://wwwdev.ebi.ac.uk/gwas/beta/rest/api/studies/"
logging_path="./logs"
APPLICATION_ROOT="/gwas/summary-statistics/api"
sqlite_path="/files/output/SumStatsMeta.db"
meta_path="./files/output/meta.h5"
snp_path="./files/output/snp.h5"
LOG_LEVEL="INFO"
LOGGER_LOG="logger.log"
LOGGER_HANDLER="logger"
LOG_CONF = {
    'version': 1,
    'disable_existing_loggers' : False,
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
    }
}
