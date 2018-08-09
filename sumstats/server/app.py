import simplejson
import sys
import logging
from logging import config
from flask import Flask, make_response
from sumstats.utils import register_logger
from sumstats.utils.properties_handler import properties
from sumstats.server.error_classes import *
import sumstats.server.api_utils as apiu
from flask import Blueprint
import sumstats.server.api_endpoints_impl as endpoints

api = Blueprint('api', __name__)

logger = logging.getLogger()

app = Flask(__name__)
app.url_map.strict_slashes = False


@api.errorhandler(APIException)
def handle_custom_api_exception(error):
    response = simplejson.dumps(error.to_dict())
    return make_response(response, error.status_code)


@api.errorhandler(404)
def not_found(error):
    return make_response(simplejson.dumps({'message': 'Page Not Found.'}), 404)


@api.errorhandler(500)
def internal_server_error(error):
    return make_response(simplejson.dumps({'message': 'Internal Server Error.'}), 500)


@api.route('/')
def root():
    return endpoints.root()


@api.route('/associations')
def get_assocs():
    return endpoints.associations()


@api.route('/traits')
def get_traits():
    return endpoints.traits()


@api.route('/traits/<string:trait>')
def get_trait(trait):
    return endpoints.trait(trait)


@api.route('/traits/<string:trait>/associations')
def get_trait_assocs(trait):
    return endpoints.trait_associations(trait)


@api.route('/studies')
def get_studies():
    return endpoints.studies()


@api.route('/traits/<string:trait>/studies')
def get_studies_for_trait(trait):
    return endpoints.studies_for_trait(trait)


@api.route('/studies/<study>')
@api.route('/traits/<string:trait>/studies/<string:study>')
def get_trait_study(study, trait=None):
    return endpoints.trait_study(study, trait)


@api.route('/studies/<study>/associations')
@api.route('/traits/<string:trait>/studies/<string:study>/associations')
def get_trait_study_assocs(study, trait=None):
    return endpoints.trait_study_associations(study, trait)


@api.route('/chromosomes')
def get_chromosomes():
    return endpoints.chromosomes()


@api.route('/chromosomes/<string:chromosome>')
def get_chromosome(chromosome):
    return endpoints.chromosome(chromosome)


@api.route('/chromosomes/<string:chromosome>/associations')
def get_chromosome_assocs(chromosome):
    return endpoints.chromosome_associations(chromosome)


@api.route('/chromosomes/<string:chromosome>/associations/<string:variant>')
def get_chromosome_variants(chromosome, variant):
    return endpoints.variants(chromosome=chromosome, variant=variant)


@api.route('/associations/<string:variant>')
def get_variant(variant):
    return endpoints.variants(variant=variant)


def _set_log_level(LOG_CONF, LOG_LEVEL):
    for handler in LOG_CONF['handlers']:
        LOG_CONF['handlers'][handler]['level'] = LOG_LEVEL
    for loggr in LOG_CONF['loggers']:
        LOG_CONF['loggers'][loggr]['level'] = LOG_LEVEL
    return LOG_CONF


def _set_log_path(properties):
    return register_logger.set_log_path(properties)


if __name__ != '__main__':
    apiu.set_properties()
    app.register_blueprint(api, url_prefix=apiu.properties.APPLICATION_ROOT)
    if '--log-level' in sys.argv:
        gunicorn_logger = logging.getLogger('gunicorn.error')
        print("Using gunicorn log level...")
        properties.LOG_LEVEL = gunicorn_logger.level
    print("Setting to logging level:", properties.LOG_LEVEL)
    properties.LOG_CONF = _set_log_level(LOG_CONF=properties.LOG_CONF, LOG_LEVEL=properties.LOG_LEVEL)
    LOG_CONF = _set_log_path(apiu.properties)
    logging.config.dictConfig(LOG_CONF)
