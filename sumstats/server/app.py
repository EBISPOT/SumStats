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
                 "maf": 0.047619,
                 "pvalue": 0.19027,
                 "variant": "chr7_27916_T_C",
                 "rsid": "rs577290214",
                 "chromosome": "7",
                 "ref": "T",
                 "beta": 0.241138,
                 "type": "SNP",
                 "position": 27916,
                 "ac": 8,
                 "study_id": "Alasoo_2018",
                 "alt": "C",
                 "an": 168,
                 "molecular_trait_id": "ENSG00000073067",
                 "gene_id": "ENSG00000073067",
                 "tissue": "CL_0000235",
                 "median_tpm": null,
                 "r2": 0.50944,
                 "_links": {
                   "study": {
                     "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                   },
                   "tissue": {
                     "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                   },
                   "variant": {
                     "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C"
                   },
                   "self": {
                     "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C?study_accession=Alasoo_2018"
                   }
                 }
               },
               "1": {
                 "maf": 0.047619,
                 "pvalue": 0.81198,
                 "variant": "chr7_27916_T_C",
                 "rsid": "rs577290214",
                 "chromosome": "7",
                 "ref": "T",
                 "beta": 0.0260822,
                 "type": "SNP",
                 "position": 27916,
                 "ac": 8,
                 "study_id": "Alasoo_2018",
                 "alt": "C",
                 "an": 168,
                 "molecular_trait_id": "ENSG00000105963",
                 "gene_id": "ENSG00000105963",
                 "tissue": "CL_0000235",
                 "median_tpm": null,
                 "r2": 0.50944,
                 "_links": {
                   "study": {
                     "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                   },
                   "tissue": {
                     "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                   },
                   "variant": {
                     "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C"
                   },
                   "self": {
                     "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C?study_accession=Alasoo_2018"
                   }
                 }
               }
             }
           },
           "_links": {
             "self": {
               "href": "https://www.ebi.ac.uk/eqtl/api/associations"
             },
             "first": {
               "href": "https://www.ebi.ac.uk/eqtl/api/associations?start=0&size=2"
             },
             "next": {
               "href": "https://www.ebi.ac.uk/eqtl/api/associations?start=2&size=2"
             }
           }
         }

     :query start: offset number. default is 0
     :query size: number of items returned. default is 20
     :query quant_method: ``ge`` (default), ``exon``, ``microarray``, ``tx`` or ``txrev`` will show you the association data for
         different quantification methods. See the API documentation for more details.
     :query p_lower: lower p-value threshold, can be expressed as a float or using mantissa and exponent
         annotation (0.001 or 1e-3 or 1E-3)
     :query p_upper: upper p-value threshold, can be expressed as a float or using mantissa and exponent
         annotation (0.001 or 1e-3 or 1E-3)
     :query molecular_trait_id: molecular phenotype identifier; will return only associations from this molecular phenotype (ENSG00000187583)
     :query gene_id: gene identifier; will return only associations with this gene id (ENSG00000073067)
     :query study: study identifer; will return only associations related to that study (Alasoo_2018)

     :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)

     :statuscode 200: no error

    """
    resp = endpoints.associations()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/associations/<string:variant_id>')
@api.route('/associations/<string:rsid>')
def get_variant(variant_id=None, rsid=None):
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

            GET /associations/rs577290214 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "maf": 0.047619,
                    "pvalue": 0.19027,
                    "variant": "chr7_27916_T_C",
                    "rsid": "rs577290214",
                    "chromosome": "7",
                    "ref": "T",
                    "beta": 0.241138,
                    "type": "SNP",
                    "position": 27916,
                    "ac": 8,
                    "study_id": "Alasoo_2018",
                    "alt": "C",
                    "an": 168,
                    "molecular_trait_id": "ENSG00000073067",
                    "gene_id": "ENSG00000073067",
                    "tissue": "CL_0000235",
                    "median_tpm": null,
                    "r2": 0.50944,
                    "_links": {
                      "study": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      },
                      "tissue": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C?study_accession=Alasoo_2018"
                      }
                    }
                  },
                  "1": {
                    "maf": 0.047619,
                    "pvalue": 0.81198,
                    "variant": "chr7_27916_T_C",
                    "rsid": "rs577290214",
                    "chromosome": "7",
                    "ref": "T",
                    "beta": 0.0260822,
                    "type": "SNP",
                    "position": 27916,
                    "ac": 8,
                    "study_id": "Alasoo_2018",
                    "alt": "C",
                    "an": 168,
                    "molecular_trait_id": "ENSG00000105963",
                    "gene_id": "ENSG00000105963",
                    "tissue": "CL_0000235",
                    "median_tpm": null,
                    "r2": 0.50944,
                    "_links": {
                      "study": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      },
                      "tissue": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C?study_accession=Alasoo_2018"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/associations"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/associations?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/associations?start=2&size=2"
                }
              }
            }


        :query start: offset number. default is 0
        :query size: number of items returned. default is 20
        :query quant_method: ``ge`` (default), ``exon``, ``microarray``, ``tx`` or ``txrev`` will show you the association data for
         different quantification methods. See the API documentation for more details.
        :query p_lower: lower p-value threshold, can be expressed as a float or using mantissa and exponent
            annotation (0.001 or 1e-3 or 1E-3)
        :query p_upper: upper p-value threshold, can be expressed as a float or using mantissa and exponent
            annotation (0.001 or 1e-3 or 1E-3)
        :query molecular_trait_id: molecular phenotype identifier; will return only associations from this molecular phenotype (ENSG00000187583)
        :query gene_id: gene identifier; will return only associations with this gene id (ENSG00000073067)
        :query study: study identifer; will return only associations related to that study (Alasoo_2018)

        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)


        :statuscode 200: no error
        :statuscode 404: not found error
    """
    identifier = variant_id if variant_id else rsid
    resp = endpoints.variants(variant=identifier)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/molecular_phenotypes')
def get_traits():
    """Molecular phenotypes

        .. :quickref: Molecular phenotypes; List all existing molecular phenotypes resources

        Lists all of the existing molecular phenotype resources.

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
                "molecular_trait_id": [
                  {
                    "molecular_trait_id": "ENSG00000187583",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000187583"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000187583/associations"
                      }
                    }
                  },
                  {
                    "molecular_trait_id": "ENSG00000227232",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000227232"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000227232/associations"
                      }
                    }
                  }
                ]
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes?start=2&size=2"
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


@api.route('/molecular_phenotypes/<string:molecular_trait_id>')
def get_trait(molecular_trait_id):
    """Molecular phenotype Resource

        .. :quickref: Molecular Phenotype Resource; Lists a specific molecular phenotype resource.

        Lists a specific molecular phenotype resource

        **Example request**:

        .. sourcecode:: http

            GET /molecular_phenotypes/ENSG00000187583 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "molecular_trait_id": "ENSG00000187583",
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000187583"
                },
                "associations": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000187583/associations"
                }
              }
            }


        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.trait(molecular_trait_id)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/molecular_phenotypes/<string:molecular_trait_id>/associations')
def get_trait_assocs(trait):
    """Search Molecular phenotype for Associations

        .. :quickref: Search Molecular phenotype for Associations; Lists associations for a specific molecular trait id.

        Lists associations for a specific molecular trait id.

        **Example request**:

        .. sourcecode:: http

            GET /molecular_phenotypes/ENSG00000105963/associations HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "an": 168,
                    "type": "SNP",
                    "r2": 0.50944,
                    "variant": "chr7_27916_T_C",
                    "alt": "C",
                    "pvalue": 0.142001,
                    "position": 27916,
                    "maf": 0.047619,
                    "study_id": "Alasoo_2018",
                    "rsid": "rs577290214",
                    "ac": 8,
                    "chromosome": "7",
                    "ref": "T",
                    "beta": -0.127039,
                    "median_tpm": null,
                    "molecular_trait_id": "ENSG00000105963",
                    "gene_id": "ENSG00000105963",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C?study_accession=Alasoo_2018"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/7/associations/chr7_27916_T_C"
                      },
                      "study": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000105963/associations"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000105963/associations?start=0&size=1"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000105963/associations?start=1&size=1"
                }
              }
            }

        :query start: offset number. default is 0
        :query size: number of items returned. default is 20
        :query quant_method: ``ge`` (default), ``exon``, ``microarray``, ``tx`` or ``txrev`` will show you the association data for
         different quantification methods. See the API documentation for more details.
        :query p_lower: lower p-value threshold, can be expressed as a float or using mantissa and exponent
             annotation (0.001 or 1e-3 or 1E-3)
        :query p_upper: upper p-value threshold, can be expressed as a float or using mantissa and exponent
             annotation (0.001 or 1e-3 or 1E-3)
        :query gene_id: gene identifier; will return only associations with this gene id (ENSG00000073067)
        :query study: study identifer; will return only associations related to that study (Alasoo_2018)

        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)
        :query variant_id: variant identifier, either rsID (rs577290214) or in the form CHR_BP_REF_ALT (chr7_27916_T_C); will only return associations with this variant

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
                      "_links": {
                        "self": {
                          "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                        },
                        "associations": {
                          "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018/associations"
                        },
                        "tissue": {
                          "href": "https://www.ebi.ac.uk/eqtl/api/tissues?study_accession=Alasoo_2018"
                        }
                      },
                      "study_accession": "Alasoo_2018"
                    }
                  ],
                  [
                    {
                      "_links": {
                        "self": {
                          "href": "https://www.ebi.ac.uk/eqtl/api/studies/BLUEPRINT"
                        },
                        "associations": {
                          "href": "https://www.ebi.ac.uk/eqtl/api/studies/BLUEPRINT/associations"
                        },
                        "tissue": {
                          "href": "https://www.ebi.ac.uk/eqtl/api/tissues?study_accession=BLUEPRINT"
                        }
                      },
                      "study_accession": "BLUEPRINT"
                    }
                  ]
                ]
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/studies"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/studies?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/studies?start=2&size=2"
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

#@api.route('/traits/<string:trait>/studies')
#def get_studies_for_trait(trait):
#    """Search Trait for Studies
#
#        .. :quickref: Search Trait for Studies; Lists studies for a specific trait.
#
#        Lists studies for a specific trait.
#
#        **Example request**:
#
#        .. sourcecode:: http
#
#            GET /traits/EFO_0003785/studies HTTP/1.1
#            Host: www.ebi.ac.uk
#
#        **Example response**:
#
#        .. sourcecode:: http
#
#            HTTP/1.1 200 OK
#            Content-Type: application/json
#
#            {
#              "_embedded": {
#                "studies": [
#                  {
#                    "study_accession": "GCST005038",
#                    "_links": {
#                      "associations": {
#                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038/associations"
#                      },
#                      "self": {
#                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies/GCST005038"
#                      },
#                      "trait": {
#                        "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785"
#                      },
#                      "gwas_catalog": {
#                        "href": "https://www.ebi.ac.uk/gwas/labs/rest/api/studies/GCST005038"
#                      }
#                    }
#                  }
#                ]
#              },
#              "_links": {
#                "self": {
#                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies"
#                },
#                "first": {
#                  "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits/EFO_0003785/studies?start=0&size=20"
#                }
#              }
#            }
#
#        :query start: offset number. default is 0
#        :query size: number of items returned. default is 20
#
#        :statuscode 200: no error
#        :statuscode 404: not found error
#    """
#    resp = endpoints.studies_for_trait(trait)
#    return Response(response=resp,
#                    status=200,
#                    mimetype="application/json")


@api.route('/tissues/<string:tissue>/studies')
def get_studies_for_tissue(tissue):
    resp = endpoints.studies_for_tissue(tissue)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/tissues/<string:tissue>/associations')
def get_tissue_assocs(tissue):
    resp = endpoints.tissue_associations(tissue)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies/<study>')
@api.route('/tissues/<string:tissue>/studies/<string:study>')
def get_tissue_study(study, tissue=None):
    resp = endpoints.tissue_study(study, tissue)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies/<study>/associations')
@api.route('/tissues/<string:tissue>/studies/<string:study>/associations')
def get_tissue_study_assocs(study, tissue=None):
    resp = endpoints.tissue_study_associations(study, tissue)
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
                    "chromosome": "1",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "10",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/10"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/10/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "11",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/11"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/11/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "12",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/12"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/12/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "13",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/13"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/13/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "14",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/14"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/14/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "15",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/15"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/15/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "16",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/16"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/16/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "17",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/17"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/17/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "18",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/18"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/18/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "19",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/19"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "2",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/2"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/2/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "20",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/20"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/20/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "21",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/21"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/21/associations"
                      }
                    }
                  },
                  {
                    "chromosome": "22",
                    "_links": {
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/22"
                      },
                      "associations": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/22/associations"
                      }
                    }
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
                  "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/11"
                },
                "associations": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/11/associations"
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
                    "an": 168,
                    "chromosome": 1,
                    "type": "INDEL",
                    "r2": 0.50127,
                    "alt": "TAA",
                    "pvalue": 0.183417,
                    "rsid": "rs529266287",
                    "maf": 0.172619,
                    "study_id": "Alasoo_2018",
                    "position": 814583,
                    "ac": 139,
                    "ref": "T",
                    "variant": "chr1_814583_T_TAA",
                    "median_tpm": null,
                    "beta": 0.116925,
                    "molecular_trait_id": "ENSG00000008128",
                    "gene_id": "ENSG00000008128",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/chr1_814583_T_TAA?study_accession=Alasoo_2018"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/chr1_814583_T_TAA"
                      },
                      "study": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      }
                    }
                  },
                  "1": {
                    "an": 168,
                    "chromosome": 1,
                    "type": "INDEL",
                    "r2": 0.50127,
                    "alt": "TAA",
                    "pvalue": 0.183417,
                    "rsid": "rs56197012",
                    "maf": 0.172619,
                    "study_id": "Alasoo_2018",
                    "position": 814583,
                    "ac": 139,
                    "ref": "T",
                    "variant": "chr1_814583_T_TAA",
                    "median_tpm": null,
                    "beta": 0.116925,
                    "molecular_trait_id": "ENSG00000008128",
                    "gene_id": "ENSG00000008128",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/chr1_814583_T_TAA?study_accession=Alasoo_2018"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/chr1_814583_T_TAA"
                      },
                      "study": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations?start=2&size=2"
                }
              }
            }



        :query start: offset number. default is 0
        :query size: number of items returned. default is 20
        :query quant_method: ``ge`` (default), ``exon``, ``microarray``, ``tx`` or ``txrev`` will show you the association data for
         different quantification methods. See the API documentation for more details.
        :query p_lower: lower p-value threshold, can be expressed as a float or using mantissa and exponent
             annotation (0.001 or 1e-3 or 1E-3)
        :query p_upper: upper p-value threshold, can be expressed as a float or using mantissa and exponent
             annotation (0.001 or 1e-3 or 1E-3)
        :query bp_lower: lower base pair location threshold, expressed as an integer
        :query bp_upper: upper base pair location threshold, expressed as an integer

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

            GET /chromosomes/1/associations/rs56197012 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "an": 168,
                    "chromosome": "1",
                    "type": "INDEL",
                    "r2": 0.50127,
                    "alt": "TAA",
                    "pvalue": 0.183417,
                    "rsid": "rs56197012",
                    "maf": 0.172619,
                    "study_id": "Alasoo_2018",
                    "position": 814583,
                    "ac": 139,
                    "ref": "T",
                    "variant": "rs56197012",
                    "median_tpm": null,
                    "beta": 0.116925,
                    "molecular_trait_id": "ENSG00000008128",
                    "gene_id": "ENSG00000008128",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012?study_accession=Alasoo_2018"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012"
                      },
                      "study": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      }
                    }
                  },
                  "1": {
                    "an": 168,
                    "chromosome": "1",
                    "type": "INDEL",
                    "r2": 0.50127,
                    "alt": "TAA",
                    "pvalue": 0.472417,
                    "rsid": "rs56197012",
                    "maf": 0.172619,
                    "study_id": "Alasoo_2018",
                    "position": 814583,
                    "ac": 139,
                    "ref": "T",
                    "variant": "rs56197012",
                    "median_tpm": null,
                    "beta": -0.0268522,
                    "molecular_trait_id": "ENSG00000008130",
                    "gene_id": "ENSG00000008130",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012?study_accession=Alasoo_2018"
                      },
                      "variant": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012"
                      },
                      "study": {
                        "href": "https://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/associations/rs56197012"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/associations/rs56197012?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/associations/rs56197012?start=2&size=2"
                }
              }
            }


        :query start: offset number. default is 0
        :query size: number of items returned. default is 20
        :query quant_method: ``ge`` (default), ``exon``, ``microarray``, ``tx`` or ``txrev`` will show you the association data for
         different quantification methods. See the API documentation for more details.
        :query p_lower: lower p-value threshold, can be expressed as a float or using mantissa and exponent
             annotation (0.001 or 1e-3 or 1E-3)
        :query p_upper: upper p-value threshold, can be expressed as a float or using mantissa and exponent
             annotation (0.001 or 1e-3 or 1E-3)

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.variants(chromosome=chromosome, variant=variant_id)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/tissues')
def get_tissues():
    resp = endpoints.tissues()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/tissues/<string:tissue>')
def get_tissue(tissue):
    resp = endpoints.tissue(tissue=tissue)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/genes')
def get_genes():
    resp = endpoints.genes()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/genes/<string:gene>')
def get_gene(gene):
    resp = endpoints.gene(gene=gene)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")

@api.route('/genes/<string:gene>/associations')
def get_gene_assocs(gene):
    resp = endpoints.gene_associations(gene=gene)
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
