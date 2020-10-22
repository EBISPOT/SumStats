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
     Can be specify by p-value cutoff threshold.

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

        Lists all of the associations of the variant requested.
        Variant id must be a valid rsid.
        Will return 404 Not Found if the variant id does not exist.
        If study_accession query parameter is specified, you will get
        a single association resource in response.
        Can be specify by p-value cutoff threshold.

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

        Lists all of the existing trait resources.

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

        Lists a specific trait resource

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
    """Search Trait for Associations

        .. :quickref: Search Trait for Associations; Lists associations for a specific trait.

        Lists associations for a specific trait.

        **Example request**:

        .. sourcecode:: http

            GET /traits/EFO_0003785/associations HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "_embedded": {
                    "associations": {
                        "0": {
                            "ci_lower": null,
                            "variant_id": "rs10875231",
                            "chromosome": 1,
                            "other_allele": "G",
                            "code": 10,
                            "odds_ratio": null,
                            "effect_allele_frequency": 0.2449,
                            "p_value": "2.826e-1",
                            "base_pair_location": 99534456,
                            "study_accession": "GCST005038",
                            "effect_allele": "T",
                            "beta": -0.0072,
                            "ci_upper": null,
                            "trait": "EFO_0003785",
                            "_links": {
                                "study": {
                                    "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005038"
                                },
                                "variant": {
                                    "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231"
                                },
                                "self": {
                                    "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?study_accession=GCST005038"
                                },
                                "trait": {
                                    "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
                                }
                            }
                        },
                        "1": {
                            "ci_lower": null,
                            "variant_id": "rs6678176",
                            "chromosome": 1,
                            "other_allele": "C",
                            "code": 10,
                            "odds_ratio": null,
                            "effect_allele_frequency": 0.3197,
                            "p_value": "2.656e-1",
                            "base_pair_location": 99535271,
                            "study_accession": "GCST005038",
                            "effect_allele": "T",
                            "beta": -0.006999999999999999,
                            "ci_upper": null,
                            "trait": "EFO_0003785",
                            "_links": {
                                "study": {
                                    "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005038"
                                },
                                "variant": {
                                    "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs6678176"
                                },
                                "self": {
                                    "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs6678176?study_accession=GCST005038"
                                },
                                "trait": {
                                    "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
                                }
                            }
                        }
                    }
                },
                "_links": {
                    "self": {
                        "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/associations"
                    },
                    "first": {
                        "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/associations?start=0&size=2"
                    },
                    "next": {
                        "href": "http://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/associations?start=2&size=2"
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
        :statuscode 404: not found error
    """
    resp = endpoints.trait_associations(trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies')
def get_studies():
    """Studies

        .. :quickref: Studies; List all existing study resources

        Lists all of the existing study resources.

        **Example request**:

        .. sourcecode:: http

            GET /studies HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "studies": [
                  [
                    {
                      "study_accession": "GCST001969",
                      "_links": {
                        "associations": {
                          "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0004326/studies/GCST001969/associations"
                        },
                        "self": {
                          "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0004326/studies/GCST001969"
                        },
                        "trait": {
                          "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0004326"
                        },
                        "gwas_catalog": {
                          "href": "https://www.ebi.ac.uk/gwas/labs/rest/api/studies/GCST001969"
                        }
                      }
                    }
                  ],
                  [
                    {
                      "study_accession": "GCST004415",
                      "_links": {
                        "associations": {
                          "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0001075/studies/GCST004415/associations"
                        },
                        "self": {
                          "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0001075/studies/GCST004415"
                        },
                        "trait": {
                          "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0001075"
                        },
                        "gwas_catalog": {
                          "href": "https://www.ebi.ac.uk/gwas/labs/rest/api/studies/GCST004415"
                        }
                      }
                    }
                  ]
                ]
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies?start=2&size=2"
                }
              }
            }

        :query start: offset number. default is 0
        :query size: number of items returned. default is 20

        :statuscode 200: no error
    """
    resp = endpoints.studies()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")

@api.route('/traits/<string:trait>/studies')
def get_studies_for_trait(trait):
    """Search Trait for Studies

        .. :quickref: Search Trait for Studies; Lists studies for a specific trait.

        Lists studies for a specific trait.

        **Example request**:

        .. sourcecode:: http

            GET /traits/EFO_0003785/studies HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "studies": [
                  {
                    "study_accession": "GCST005038",
                    "_links": {
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038/associations"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038"
                      },
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
                      },
                      "gwas_catalog": {
                        "href": "https://www.ebi.ac.uk/gwas/labs/rest/api/studies/GCST005038"
                      }
                    }
                  }
                ]
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies?start=0&size=20"
                }
              }
            }

        :query start: offset number. default is 0
        :query size: number of items returned. default is 20

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.studies_for_trait(trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies/<study>')
@api.route('/traits/<string:trait>/studies/<string:study>')
def get_trait_study(study, trait=None):
    """Study Resource

        .. :quickref: Study Resource; Lists resources for a specific study. Will return 404 Not Found if the study accession does not exist.

        Lists resources for a specific study.

        **Example request**:

        .. sourcecode:: http

            GET /studies/GCST005038 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "study_accession": "GCST005038",
              "_links": {
                "associations": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038/associations"
                },
                "self": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038"
                },
                "trait": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
                },
                "gwas_catalog": {
                  "href": "https://www.ebi.ac.uk/gwas/labs/rest/api/studies/GCST005038"
                }
              }
            }

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.trait_study(study, trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/study_list')
def get_all_studies():

    resp = endpoints.study_list()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies/<study>/associations')
@api.route('/traits/<string:trait>/studies/<string:study>/associations')
def get_trait_study_assocs(study, trait=None):
    """Search Study Associations

        .. :quickref: Search Study Associations; Returns associations for a specific study. Will return 404 Not Found if the study accession does not exist.

        Returns associations for a specific study.

        **Example request**:

        .. sourcecode:: http

            GET /studies/GCST005038/associations HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "ci_lower": null,
                    "variant_id": "rs10875231",
                    "chromosome": 1,
                    "other_allele": "G",
                    "code": 10,
                    "odds_ratio": null,
                    "effect_allele_frequency": 0.2449,
                    "p_value": "2.826e-1",
                    "base_pair_location": 99534456,
                    "study_accession": "GCST005038",
                    "effect_allele": "T",
                    "beta": -0.0072,
                    "ci_upper": null,
                    "trait": "EFO_0003785",
                    "_links": {
                      "study": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005038"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?study_accession=GCST005038"
                      },
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
                      }
                    }
                  },
                  "1": {
                    "ci_lower": null,
                    "variant_id": "rs6678176",
                    "chromosome": 1,
                    "other_allele": "C",
                    "code": 10,
                    "odds_ratio": null,
                    "effect_allele_frequency": 0.3197,
                    "p_value": "2.656e-1",
                    "base_pair_location": 99535271,
                    "study_accession": "GCST005038",
                    "effect_allele": "T",
                    "beta": -0.006999999999999999,
                    "ci_upper": null,
                    "trait": "EFO_0003785",
                    "_links": {
                      "study": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005038"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs6678176"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs6678176?study_accession=GCST005038"
                      },
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038/associations"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038/associations?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038/associations?start=2&size=2"
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
        :statuscode 404: not found error
    """
    resp = endpoints.trait_study_associations(study, trait)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/chromosomes')
def get_chromosomes():
    """Chromosomes

        .. :quickref: Chromosomes; List all chromosome resources

        Lists all chromosome resources. Note that chromosomes values 'X', 'Y' and 'MT' are mapped to 23, 24 and 25, respectively.

        **Example request**:

        .. sourcecode:: http

            GET /chromosomes HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "chromosomes": [
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations"
                      }
                    },
                    "chromosome": 1
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/2"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/2/associations"
                      }
                    },
                    "chromosome": 2
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/3"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/3/associations"
                      }
                    },
                    "chromosome": 3
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/4"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/4/associations"
                      }
                    },
                    "chromosome": 4
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/5"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/5/associations"
                      }
                    },
                    "chromosome": 5
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/6"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/6/associations"
                      }
                    },
                    "chromosome": 6
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/7"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/7/associations"
                      }
                    },
                    "chromosome": 7
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/8"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/8/associations"
                      }
                    },
                    "chromosome": 8
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/9"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/9/associations"
                      }
                    },
                    "chromosome": 9
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/10"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/10/associations"
                      }
                    },
                    "chromosome": 10
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/11"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/11/associations"
                      }
                    },
                    "chromosome": 11
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/12"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/12/associations"
                      }
                    },
                    "chromosome": 12
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/13"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/13/associations"
                      }
                    },
                    "chromosome": 13
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/14"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/14/associations"
                      }
                    },
                    "chromosome": 14
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/15"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/15/associations"
                      }
                    },
                    "chromosome": 15
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/16"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/16/associations"
                      }
                    },
                    "chromosome": 16
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/17"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/17/associations"
                      }
                    },
                    "chromosome": 17
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/18"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/18/associations"
                      }
                    },
                    "chromosome": 18
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/19"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/19/associations"
                      }
                    },
                    "chromosome": 19
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/20"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/20/associations"
                      }
                    },
                    "chromosome": 20
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/21"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/21/associations"
                      }
                    },
                    "chromosome": 21
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/22"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/22/associations"
                      }
                    },
                    "chromosome": 22
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/23"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/23/associations"
                      }
                    },
                    "chromosome": 23
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/24"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/24/associations"
                      }
                    },
                    "chromosome": 24
                  }
                ]
              }
            }

        :statuscode 200: no error
    """
    resp = endpoints.chromosomes()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/chromosomes/<string:chromosome>')
def get_chromosome(chromosome):
    """Chromosome Resource

        .. :quickref: Chromosome Resource; List a specific chromosome resource

        List a specific chromosome resource. Note that chromosomes values 'X', 'Y' and 'MT' are mapped to 23, 24 and 25, respectively.

        **Example request**:

        .. sourcecode:: http

            GET /chromosomes/11 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/11"
                },
                "associations": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/11/associations"
                }
              },
              "chromosome": "11"
            }

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.chromosome(chromosome)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/chromosomes/<string:chromosome>/associations')
def get_chromosome_assocs(chromosome):
    """Search Chromosome Associations

        .. :quickref: Search Chromosome Associations; Returns associations for a specific chromosome. Will return 404 Not Found if the chromosome value does not exist.

        Returns associations for a specific chromosome.

        **Example request**:

        .. sourcecode:: http

            GET /chromosomes/1/associations HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "ci_lower": null,
                    "base_pair_location": 11820711,
                    "other_allele": "A",
                    "code": 10,
                    "odds_ratio": null,
                    "effect_allele_frequency": 0.09228,
                    "ci_upper": null,
                    "p_value": "1.86278e-2",
                    "variant_id": "rs146777460",
                    "study_accession": "GCST005353",
                    "effect_allele": "G",
                    "beta": 0.45443999999999996,
                    "chromosome": 1,
                    "trait": "EFO_0008531",
                    "_links": {
                      "study": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005353"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs146777460"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs146777460?study_accession=GCST005353"
                      },
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0008531"
                      }
                    }
                  },
                  "1": {
                    "ci_lower": null,
                    "base_pair_location": 11844019,
                    "other_allele": "T",
                    "code": 10,
                    "odds_ratio": null,
                    "effect_allele_frequency": 0.24731999999999998,
                    "ci_upper": null,
                    "p_value": "2.100256e-2",
                    "variant_id": "rs198358",
                    "study_accession": "GCST005353",
                    "effect_allele": "C",
                    "beta": 0.2694,
                    "chromosome": 1,
                    "trait": "EFO_0008531",
                    "_links": {
                      "study": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005353"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs198358"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs198358?study_accession=GCST005353"
                      },
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0008531"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations?bp_upper=11850510"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations?start=0&size=2&bp_upper=11850510"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations?start=2&size=2&bp_upper=11850510"
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
        :query bp_lower: lower base pair location threshold, expressed as an integer
        :query bp_upper: upper base pair location threshold, expressed as an integer
        :query study_accession: accession ID of the study to query
        :query trait: trait ID of of the trait to query

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.chromosome_associations(chromosome)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/chromosomes/<string:chromosome>/associations/<string:variant_id>')
def get_chromosome_variants(chromosome, variant_id):
    """Search Variant on Chromosome

        .. :quickref: Search Variant on Chromosome; Lists all of the available associations of a specific variant.

        Lists all of the associations of the variant requested.
        Variant id must be a valid rsid.
        Will return 404 Not Found if the variant id does not exist.
        Can specify by p-value cutoff threshold.
        The response should be identical to the /associations/<string:variant_id> but the query time may be faster.

        **Example request**:

        .. sourcecode:: http

            GET /chromosomes/1/associations/rs10875231 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "ci_lower": null,
                    "chromosome": 1,
                    "other_allele": "G",
                    "code": 10,
                    "odds_ratio": null,
                    "effect_allele_frequency": 0.28367,
                    "ci_upper": null,
                    "p_value": "5.837561e-1",
                    "base_pair_location": 99534456,
                    "study_accession": "GCST005353",
                    "effect_allele": "T",
                    "beta": 0.06794,
                    "variant_id": "rs10875231",
                    "trait": "EFO_0008531",
                    "_links": {
                      "study": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST005353"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?study_accession=GCST005353"
                      },
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0008531"
                      }
                    }
                  },
                  "1": {
                    "ci_lower": null,
                    "chromosome": 1,
                    "other_allele": "G",
                    "code": 10,
                    "odds_ratio": null,
                    "effect_allele_frequency": 0.2665,
                    "ci_upper": null,
                    "p_value": "5.167e-1",
                    "base_pair_location": 99534456,
                    "study_accession": "GCST001969",
                    "effect_allele": "T",
                    "beta": -0.0375,
                    "variant_id": "rs10875231",
                    "trait": "EFO_0004326",
                    "_links": {
                      "study": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies/GCST001969"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?study_accession=GCST001969"
                      },
                      "trait": {
                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0004326"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations/rs10875231?start=2&size=2"
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
        :query study_accession: accession ID of the study to query
        :query trait: trait ID of of the trait to query

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.variants(chromosome=chromosome, variant=variant_id)
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
