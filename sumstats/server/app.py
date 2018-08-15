import simplejson
import sys
import logging
from logging import config
from flask import Flask, make_response, Response
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
    response = error.to_dict()
    response['status'] = error.status_code
    response = simplejson.dumps(response)
    resp = make_response(response, error.status_code)
    resp.mimetype = 'application/json'
    return resp


@api.errorhandler(404)
def not_found(error):
    response = {'message': 'Page Not Found.', 'status': 404, 'error': 'Page Not Found'}
    response = simplejson.dumps(response)
    resp = make_response(response, error.status_code)
    resp.mimetype = 'application/json'
    return resp


@api.errorhandler(500)
def internal_server_error(error):
    response = {'message': 'Internal Server Error.', 'status': 500, 'error': 'Internal Server Error'}
    response = simplejson.dumps(response)
    resp = make_response(response, error.status_code)
    resp.mimetype = 'application/json'
    return resp


@api.route('/')
def root():
    resp = endpoints.root()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/associations')
def get_assocs():
    """Associations

    .. :quickref: Associations; Lists all of the available associations.

    Lists all of the available associations that are loaded into the database.

    **Example request**:

    .. sourcecode:: http

        GET /associations HTTP/1.1
        Host: www.ebi.ac.uk

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
          "_embedded": {
            "associations": {
              "0": {
                "p_value": "2.826e-1",
                "odds_ratio": null,
                "effect_allele_frequency": 0.2449,
                "chromosome": 1,
                "beta": -0.0072,
                "other_allele": "G",
                "ci_upper": null,
                "study_accession": "GCST005038",
                "effect_allele": "T",
                "variant_id": "rs10875231",
                "code": 10,
                "ci_lower": null,
                "base_pair_location": 99534456,
                "trait": "EFO_0003785",
                "_links": {
                  "trait": {
                    "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
                  },
                  "study": {
                    "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005038"
                  },
                  "self": {
                    "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?study_accession=GCST005038"
                  },
                  "variant": {
                    "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231"
                  }
                }
              },
              "1": {
                "p_value": "2.656e-1",
                "odds_ratio": null,
                "effect_allele_frequency": 0.3197,
                "chromosome": 1,
                "beta": -0.006999999999999999,
                "other_allele": "C",
                "ci_upper": null,
                "study_accession": "GCST005038",
                "effect_allele": "T",
                "variant_id": "rs6678176",
                "code": 10,
                "ci_lower": null,
                "base_pair_location": 99535271,
                "trait": "EFO_0003785",
                "_links": {
                  "trait": {
                    "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
                  },
                  "study": {
                    "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005038"
                  },
                  "self": {
                    "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs6678176?study_accession=GCST005038"
                  },
                  "variant": {
                    "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs6678176"
                  }
                }
              }
            }
          },
          "_links": {
            "self": {
              "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations"
            },
            "first": {
              "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations?size=2&start=0"
            },
            "next": {
              "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations?size=2&start=2"
            }
          }
        }


    :query start: offset number. default is 0
    :query size: number of items returned. default is 20
    :query reveal: ``raw`` or ``all`` will show you the raw association data or both the harmonised and
        raw association data respectively.
    :query p_lower: lower p-value threshold, can be expressed as a float or using mantissa and exponent
        annotation (0.001 or 1e-3 or 1E-3)
    :query p_upper: upper p-value threshold, can be expressed as a float or using mantissa and exponent
        annotation (0.001 or 1e-3 or 1E-3)

    :statuscode 200: no error
    """
    resp = endpoints.associations()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/associations/<string:variant_id>')
def get_variant(variant_id):
    """Search Variant Associations

        .. :quickref: Variant Associations; Lists all of the available associations of a specific variant.

        **Example request**:

        .. sourcecode:: http

            GET /associations/rs10875231 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "p_value": "5.837561e-1",
                    "ci_lower": null,
                    "odds_ratio": null,
                    "effect_allele_frequency": 0.28367,
                    "chromosome": 1,
                    "beta": 0.06794,
                    "other_allele": "G",
                    "ci_upper": null,
                    "study_accession": "GCST005353",
                    "effect_allele": "T",
                    "code": 10,
                    "base_pair_location": 99534456,
                    "trait": "EFO_0008531",
                    "variant_id": "rs10875231",
                    "_links": {
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0008531"
                      },
                      "study": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005353"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?study_accession=GCST005353"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231"
                      }
                    }
                  },
                  "1": {
                    "p_value": "5.167e-1",
                    "ci_lower": null,
                    "odds_ratio": null,
                    "effect_allele_frequency": 0.2665,
                    "chromosome": 1,
                    "beta": -0.0375,
                    "other_allele": "G",
                    "ci_upper": null,
                    "study_accession": "GCST001969",
                    "effect_allele": "T",
                    "code": 10,
                    "base_pair_location": 99534456,
                    "trait": "EFO_0004326",
                    "variant_id": "rs10875231",
                    "_links": {
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0004326"
                      },
                      "study": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST001969"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?study_accession=GCST001969"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations/rs10875231"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations/rs10875231?size=2&start=0"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations/rs10875231?size=2&start=2"
                }
              }
            }

        :query start: offset number. default is 0
        :query size: number of items returned. default is 20
        :query reveal: ``raw`` or ``all`` will show you the raw association data or both the harmonised and
            raw association data respectively.
        :query p_lower: lower p-value threshold, can be expressed as a float or using mantissa and exponent
            annotation (0.001 or 1e-3 or 1E-3)
        :query p_upper: upper p-value threshold, can be expressed as a float or using mantissa and exponent
            annotation (0.001 or 1e-3 or 1E-3)
        :query study_accession: the accession of a specific study; will return only associations related to that study

        :statuscode 200: no error
        :statuscode 404: not found error
        """
    resp = endpoints.variants(variant=variant_id)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/traits')
def get_traits():
    """Traits

        .. :quickref: Traits; List all existing trait resources

        **Example request**:

        .. sourcecode:: http

            GET /traits HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
             "_embedded": {
               "traits": [
                 {
                   "trait": "EFO_0008531",
                   "_links": {
                     "self": {
                       "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0008531"
                     },
                     "ols": {
                       "href": "https://www.ebi.ac.uk/ols/api/terms?id=EFO_0008531"
                     },
                     "studies": {
                       "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0008531/studies"
                     },
                     "associations": {
                       "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0008531/associations"
                     }
                   }
                 }
               ]
             },
             "_links": {
               "self": {
                 "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits"
               },
               "first": {
                 "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits?size=20&start=0"
               }
             }
            }

        :query start: offset number. default is 0
        :query size: number of items returned. default is 20

        :statuscode 200: no error
    """
    resp = endpoints.traits()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/traits/<string:trait>')
def get_trait(trait):
    """Trait Resource

    .. :quickref: Trait Resource; Lists a specific trait resource.

    **Example request**:

    .. sourcecode:: http

        GET /traits/EFO_0003785 HTTP/1.1
        Host: www.ebi.ac.uk

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
          "trait": "EFO_0003785",
          "_links": {
            "studies": {
              "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies"
            },
            "associations": {
              "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/associations"
            },
            "self": {
              "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
            },
            "ols": {
              "href": "https://www.ebi.ac.uk/ols/api/terms?id=EFO_0003785"
            }
          }
        }

    :statuscode 200: no error
    :statuscode 404: not found error
    """
    resp = endpoints.trait(trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/traits/<string:trait>/associations')
def get_trait_assocs(trait):
    resp = endpoints.trait_associations(trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies')
def get_studies():
    resp = endpoints.studies()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/traits/<string:trait>/studies')
def get_studies_for_trait(trait):
    resp = endpoints.studies_for_trait(trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies/<study>')
@api.route('/traits/<string:trait>/studies/<string:study>')
def get_trait_study(study, trait=None):
    resp = endpoints.trait_study(study, trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies/<study>/associations')
@api.route('/traits/<string:trait>/studies/<string:study>/associations')
def get_trait_study_assocs(study, trait=None):
    resp = endpoints.trait_study_associations(study, trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/chromosomes')
def get_chromosomes():
    resp = endpoints.chromosomes()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/chromosomes/<string:chromosome>')
def get_chromosome(chromosome):
    resp = endpoints.chromosome(chromosome)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/chromosomes/<string:chromosome>/associations')
def get_chromosome_assocs(chromosome):
    resp = endpoints.chromosome_associations(chromosome)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/chromosomes/<string:chromosome>/associations/<string:variant>')
def get_chromosome_variants(chromosome, variant):
    resp = endpoints.variants(chromosome=chromosome, variant=variant)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


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
