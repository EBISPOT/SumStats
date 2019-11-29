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
                     "alt": "G",
                     "condition": "naive",
                     "rsid": "rs200141179",
                     "condition_label": "naive",
                     "ac": 240,
                     "position": 230130,
                     "chromosome": "19",
                     "an": 972,
                     "qtl_group": "brain",
                     "beta": -0.0529243,
                     "r2": 0.48226,
                     "variant": "chr19_230130_GATC_G",
                     "study_id": "BrainSeq",
                     "ref": "GATC",
                     "tissue_label": "brain",
                     "type": "INDEL",
                     "maf": 0.246914,
                     "median_tpm": 12.272,
                     "pvalue": 0.0166984,
                     "molecular_trait_id": "ENSG00000011304",
                     "gene_id": "ENSG00000011304",
                     "tissue": "UBERON_0009834",
                     "_links": {
                       "self": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G?study_accession=BrainSeq"
                       },
                       "tissue": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                       },
                       "variant": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G"
                       },
                       "study": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
                       }
                     }
                   },
                   "1": {
                     "alt": "G",
                     "condition": "naive",
                     "rsid": "rs200141179",
                     "condition_label": "naive",
                     "ac": 240,
                     "position": 230130,
                     "chromosome": "19",
                     "an": 972,
                     "qtl_group": "brain",
                     "beta": 0.0340718,
                     "r2": 0.48226,
                     "variant": "chr19_230130_GATC_G",
                     "study_id": "BrainSeq",
                     "ref": "GATC",
                     "tissue_label": "brain",
                     "type": "INDEL",
                     "maf": 0.246914,
                     "median_tpm": 27.623,
                     "pvalue": 0.424836,
                     "molecular_trait_id": "ENSG00000129951",
                     "gene_id": "ENSG00000129951",
                     "tissue": "UBERON_0009834",
                     "_links": {
                       "self": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G?study_accession=BrainSeq"
                       },
                       "tissue": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                       },
                       "variant": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G"
                       },
                       "study": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
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
    
        :query quant_method: ``ge`` (default), ``exon``, ``microarray``, ``tx`` or ``txrev`` will show you the association data for
            different quantification methods. See the API documentation for more details.
        :query p_lower: lower p-value threshold, can be expressed as a float or using mantissa and exponent
            annotation (0.001 or 1e-3 or 1E-3)
        :query p_upper: upper p-value threshold, can be expressed as a float or using mantissa and exponent
            annotation (0.001 or 1e-3 or 1E-3)
        :query molecular_trait_id: molecular phenotype identifier; will return only associations from this molecular phenotype (ENSG00000187583)
        :query variant_id: variant identifier, either rsID (rs577290214) or in the form CHR_BP_REF_ALT (chr7_27916_T_C); will only return associations with this variant
        :query qtl_group: QTL group/context
            so for any study, you can also specify a ``qtl_group``, which will filter to only return data from this context
        :query gene_id: gene identifier; will return only associations with this gene id (ENSG00000073067)
        :query study: study identifer; will return only associations related to that study (Alasoo_2018)
        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)
        :query start: offset number. default is 0
        :query size: number of items returned. default is 20, max is 1000.
        :query paginate: Flag whether the response should be paginated or not. Boolean `True` (default) or `False`
        :statuscode 200: no error
        :statuscode 404: not found error
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

            GET /associations/rs200141179 HTTP/1.1
            Host: www.ebi.ac.uk

        .. sourcecode:: http

            GET /associations/chr19_230130_GATC_G HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
               "_embedded": {
                 "associations": {
                   "0": {
                     "alt": "G",
                     "condition": "naive",
                     "rsid": "rs200141179",
                     "condition_label": "naive",
                     "ac": 240,
                     "position": 230130,
                     "chromosome": "19",
                     "an": 972,
                     "qtl_group": "brain",
                     "beta": -0.0529243,
                     "r2": 0.48226,
                     "variant": "chr19_230130_GATC_G",
                     "study_id": "BrainSeq",
                     "ref": "GATC",
                     "tissue_label": "brain",
                     "type": "INDEL",
                     "maf": 0.246914,
                     "median_tpm": 12.272,
                     "pvalue": 0.0166984,
                     "molecular_trait_id": "ENSG00000011304",
                     "gene_id": "ENSG00000011304",
                     "tissue": "UBERON_0009834",
                     "_links": {
                       "self": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G?study_accession=BrainSeq"
                       },
                       "tissue": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                       },
                       "variant": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G"
                       },
                       "study": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
                       }
                     }
                   },
                   "1": {
                     "alt": "G",
                     "condition": "naive",
                     "rsid": "rs200141179",
                     "condition_label": "naive",
                     "ac": 240,
                     "position": 230130,
                     "chromosome": "19",
                     "an": 972,
                     "qtl_group": "brain",
                     "beta": 0.0340718,
                     "r2": 0.48226,
                     "variant": "chr19_230130_GATC_G",
                     "study_id": "BrainSeq",
                     "ref": "GATC",
                     "tissue_label": "brain",
                     "type": "INDEL",
                     "maf": 0.246914,
                     "median_tpm": 27.623,
                     "pvalue": 0.424836,
                     "molecular_trait_id": "ENSG00000129951",
                     "gene_id": "ENSG00000129951",
                     "tissue": "UBERON_0009834",
                     "_links": {
                       "self": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G?study_accession=BrainSeq"
                       },
                       "tissue": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                       },
                       "variant": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G"
                       },
                       "study": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
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
        :query qtl_group: QTL group/context
        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)
        :query paginate: Flag whether the response should be paginated or not. Boolean `True` (default) or `False`


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
def get_trait_assocs(molecular_trait_id):
    """Search Molecular phenotype for Associations

        .. :quickref: Search Molecular phenotype for Associations; Lists associations for a specific molecular trait id.

        Lists associations for a specific molecular trait id.

        **Example request**:

        .. sourcecode:: http

            GET /molecular_phenotypes/ENSG00000011304/associations HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
               "_embedded": {
                 "associations": {
                   "0": {
                     "alt": "G",
                     "condition": "naive",
                     "rsid": "rs200141179",
                     "condition_label": "naive",
                     "ac": 240,
                     "position": 230130,
                     "chromosome": "19",
                     "an": 972,
                     "qtl_group": "brain",
                     "beta": -0.0529243,
                     "r2": 0.48226,
                     "variant": "chr19_230130_GATC_G",
                     "study_id": "BrainSeq",
                     "ref": "GATC",
                     "tissue_label": "brain",
                     "type": "INDEL",
                     "maf": 0.246914,
                     "median_tpm": 12.272,
                     "pvalue": 0.0166984,
                     "molecular_trait_id": "ENSG00000011304",
                     "gene_id": "ENSG00000011304",
                     "tissue": "UBERON_0009834",
                     "_links": {
                       "self": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G?study_accession=BrainSeq"
                       },
                       "tissue": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                       },
                       "variant": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_230130_GATC_G"
                       },
                       "study": {
                         "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
                       }
                     }
                   },
               "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000011304/associations"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000011304/associations?start=0&size=1"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes/ENSG00000011304/associations?start=1&size=1"
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
        :query qtl_group: QTL group/context
        :query paginate: Flag whether the response should be paginated or not. Boolean `True` (default) or `False`
        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)
        :query variant_id: variant identifier, either rsID (rs577290214) or in the form CHR_BP_REF_ALT (chr7_27916_T_C); will only return associations with this variant

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.trait_associations(trait=molecular_trait_id)
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
    """Studies for tissues

        .. :quickref: Studies for tissues; List all existing study resources for a given tissue ontology

        Lists all of the existing study resources.

        **Example request**:

        .. sourcecode:: http

            GET /tissues/CL_0000235/studies HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "studies": [
                  {
                    "_links": {
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies/Alasoo_2018"
                      },
                      "associations": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies/Alasoo_2018/associations"
                      },
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues?study_accession=Alasoo_2018"
                      }
                    },
                    "study_accession": "Alasoo_2018"
                  },
                  {
                    "_links": {
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies/Nedelec_2016"
                      },
                      "associations": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies/Nedelec_2016/associations"
                      },
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues?study_accession=Nedelec_2016"
                      }
                    },
                    "study_accession": "Nedelec_2016"
                  }
                ]
              },
              "_links": {
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies"
                },
                "first": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies?size=20&start=0"
                }
              }
            }

        :query start: offset number. default is 0
        :query size: number of items returned. default is 20

        :statuscode 200: no error
    """
    resp = endpoints.studies_for_tissue(tissue)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/tissues/<string:tissue>/associations')
def get_tissue_assocs(tissue):
    """Search Tissue for Associations

        .. :quickref: Search Tissue/Cell type for Associations; Lists associations for a specific tissue ontology.

        Lists associations for a specific tissue ontology

        **Example request**:

        .. sourcecode:: http

            GET /tissues/CL_0000235/associations HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "condition_label": "IFNg_18h+Salmonella_5h",
                    "alt": "A",
                    "condition": "IFNg+Salmonella",
                    "rsid": "rs201551942",
                    "r2": 0.44038,
                    "ac": 64,
                    "position": 229783,
                    "chromosome": "19",
                    "an": 168,
                    "qtl_group": "macrophage_IFNg+Salmonella",
                    "beta": 0.0245131,
                    "median_tpm": null,
                    "variant": "chr19_229783_G_A",
                    "study_id": "Alasoo_2018",
                    "ref": "G",
                    "tissue_label": "macrophage",
                    "type": "SNP",
                    "maf": 0.380952,
                    "pvalue": 0.5004,
                    "molecular_trait_id": "ENSG00000011304",
                    "gene_id": "ENSG00000011304",
                    "tissue": "CL_0000235",
                    "_links": {
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_229783_G_A?study_accession=Alasoo_2018"
                      },
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_229783_G_A"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      }
                    }
                  },
                  "1": {
                    "condition_label": "IFNg_18h+Salmonella_5h",
                    "alt": "A",
                    "condition": "IFNg+Salmonella",
                    "rsid": "rs201551942",
                    "r2": 0.44038,
                    "ac": 64,
                    "position": 229783,
                    "chromosome": "19",
                    "an": 168,
                    "qtl_group": "macrophage_IFNg+Salmonella",
                    "beta": -0.0685795,
                    "median_tpm": null,
                    "variant": "chr19_229783_G_A",
                    "study_id": "Alasoo_2018",
                    "ref": "G",
                    "tissue_label": "macrophage",
                    "type": "SNP",
                    "maf": 0.380952,
                    "pvalue": 0.0528997,
                    "molecular_trait_id": "ENSG00000099817",
                    "gene_id": "ENSG00000099817",
                    "tissue": "CL_0000235",
                    "_links": {
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_229783_G_A?study_accession=Alasoo_2018"
                      },
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_229783_G_A"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/associations"
                },
                "first": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/associations?size=2&start=0"
                },
                "next": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/associations?size=2&start=2"
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
        :query qtl_group: QTL group/context
        :query paginate: Flag whether the response should be paginated or not. Boolean `True` (default) or `False`
        :query molecular_trait_id: molecular phenotype identifier; will return only associations from this molecular phenotype (ENSG00000187583)
        :query variant_id: variant identifier, either rsID (rs577290214) or in the form CHR_BP_REF_ALT (chr7_27916_T_C); will only return associations with this variant

        :statuscode 200: no error
        :statuscode 404: not found error

    """
    resp = endpoints.tissue_associations(tissue)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies/<string:study>')
@api.route('/tissues/<string:tissue>/studies/<string:study>')
def get_tissue_study(study, tissue=None):
    """Study

        .. :quickref: Study; Lists a specific study resource

         Lists a specific study or tissue/study resource.

        **Example request**:

        .. sourcecode:: http

            GET /studies/Alasoo_2018 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            
            {
              "study_accession": "Alasoo_2018",
              "_links": {
                "associations": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018/associations"
                },
                "tissue": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues?study_accession=Alasoo_2018"
                },
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                }
              }
            }

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.tissue_study(study, tissue)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/studies/<study>/associations')
@api.route('/tissues/<string:tissue>/studies/<string:study>/associations')
def get_tissue_study_assocs(study, tissue=None):
    """Search Study for Associations

        .. :quickref: Search Study for Associations; Lists associations for a specific study.

        Lists associations for a specific study.

        **Example request**:

        .. sourcecode:: http

            GET /studies/Alasoo_2018/associations HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "study_id": "Alasoo_2018",
                    "r2": 0.44038,
                    "median_tpm": null,
                    "type": "SNP",
                    "condition_label": "IFNg_18h+Salmonella_5h",
                    "chromosome": "19",
                    "maf": 0.380952,
                    "beta": 0.0245131,
                    "condition": "IFNg+Salmonella",
                    "alt": "A",
                    "ac": 64,
                    "an": 168,
                    "qtl_group": "macrophage_IFNg+Salmonella",
                    "ref": "G",
                    "pvalue": 0.5004,
                    "position": 229783,
                    "variant": "chr19_229783_G_A",
                    "tissue_label": "macrophage",
                    "rsid": "rs201551942",
                    "molecular_trait_id": "ENSG00000011304",
                    "gene_id": "ENSG00000011304",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_229783_G_A?study_accession=Alasoo_2018"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      },
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_229783_G_A"
                      }
                    }
                  },
                  "1": {
                    "study_id": "Alasoo_2018",
                    "r2": 0.44038,
                    "median_tpm": null,
                    "type": "SNP",
                    "condition_label": "IFNg_18h+Salmonella_5h",
                    "chromosome": "19",
                    "maf": 0.380952,
                    "beta": -0.0685795,
                    "condition": "IFNg+Salmonella",
                    "alt": "A",
                    "ac": 64,
                    "an": 168,
                    "qtl_group": "macrophage_IFNg+Salmonella",
                    "ref": "G",
                    "pvalue": 0.0528997,
                    "position": 229783,
                    "variant": "chr19_229783_G_A",
                    "tissue_label": "macrophage",
                    "rsid": "rs201551942",
                    "molecular_trait_id": "ENSG00000099817",
                    "gene_id": "ENSG00000099817",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_229783_G_A?study_accession=Alasoo_2018"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/Alasoo_2018"
                      },
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/19/associations/chr19_229783_G_A"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies/Alasoo_2018/associations"
                },
                "first": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies/Alasoo_2018/associations?start=0&size=2"
                },
                "next": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235/studies/Alasoo_2018/associations?start=2&size=2"
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
        :query molecular_trait_id: molecular phenotype identifier; will return only associations from this molecular phenotype (ENSG00000187583)
        :query qtl_group: QTL group/context
        :query paginate: Flag whether the response should be paginated or not. Boolean `True` (default) or `False`
        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)
        :query variant_id: variant identifier, either rsID (rs577290214) or in the form CHR_BP_REF_ALT (chr7_27916_T_C); will only return associations with this variant

        :statuscode 200: no error
        :statuscode 404: not found error
            
    """
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
                    "an": 972,
                    "beta": 0.0866221,
                    "median_tpm": 0.991,
                    "qtl_group": "brain",
                    "r2": 0.9107,
                    "condition": "naive",
                    "variant": "chr1_1053768_G_A",
                    "tissue_label": "brain",
                    "study_id": "BrainSeq",
                    "condition_label": "naive",
                    "ref": "G",
                    "alt": "A",
                    "position": 1053768,
                    "pvalue": 0.483624,
                    "maf": 0.0123457,
                    "type": "SNP",
                    "ac": 12,
                    "rsid": "rs115061121",
                    "chromosome": 1,
                    "molecular_trait_id": "ENSG00000008128",
                    "gene_id": "ENSG00000008128",
                    "tissue": "UBERON_0009834",
                    "_links": {
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/chr1_1053768_G_A"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
                      },
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/chr1_1053768_G_A?study_accession=BrainSeq"
                      }
                    }
                  },
                  "1": {
                    "an": 972,
                    "beta": 0.0304911,
                    "median_tpm": 21.145,
                    "qtl_group": "brain",
                    "r2": 0.9107,
                    "condition": "naive",
                    "variant": "chr1_1053768_G_A",
                    "tissue_label": "brain",
                    "study_id": "BrainSeq",
                    "condition_label": "naive",
                    "ref": "G",
                    "alt": "A",
                    "position": 1053768,
                    "pvalue": 0.468078,
                    "maf": 0.0123457,
                    "type": "SNP",
                    "ac": 12,
                    "rsid": "rs115061121",
                    "chromosome": 1,
                    "molecular_trait_id": "ENSG00000197530",
                    "gene_id": "ENSG00000197530",
                    "tissue": "UBERON_0009834",
                    "_links": {
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/chr1_1053768_G_A"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
                      },
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/chr1_1053768_G_A?study_accession=BrainSeq"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations"
                },
                "first": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations?size=2&start=0"
                },
                "next": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations?size=2&start=2"
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
        :query molecular_trait_id: molecular phenotype identifier; will return only associations from this molecular phenotype (ENSG00000187583)
        :query gene_id: gene identifier; will return only associations with this gene id (ENSG00000073067)
        :query study: study identifer; will return only associations related to that study (Alasoo_2018)
        :query qtl_group: QTL group/context
        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)
        :query paginate: Flag whether the response should be paginated or not. Boolean `True` (default) or `False`

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
                    "study_id": "Nedelec_2016",
                    "r2": 0.7364,
                    "median_tpm": 148.732,
                    "type": "INDEL",
                    "condition_label": "naive",
                    "chromosome": "1",
                    "maf": 0.190184,
                    "beta": -0.0255253,
                    "condition": "naive",
                    "alt": "TAA",
                    "ac": 264,
                    "an": 326,
                    "qtl_group": "macrophage_naive",
                    "ref": "T",
                    "pvalue": 0.24666,
                    "position": 814583,
                    "variant": "rs56197012",
                    "tissue_label": "macrophage",
                    "rsid": "rs56197012",
                    "molecular_trait_id": "ENSG00000078808",
                    "gene_id": "ENSG00000078808",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012?study_accession=Nedelec_2016"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/Nedelec_2016"
                      },
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012"
                      }
                    }
                  },
                  "1": {
                    "study_id": "Nedelec_2016",
                    "r2": 0.7364,
                    "median_tpm": 39.017,
                    "type": "INDEL",
                    "condition_label": "naive",
                    "chromosome": "1",
                    "maf": 0.190184,
                    "beta": 0.018958,
                    "condition": "naive",
                    "alt": "TAA",
                    "ac": 264,
                    "an": 326,
                    "qtl_group": "macrophage_naive",
                    "ref": "T",
                    "pvalue": 0.711897,
                    "position": 814583,
                    "variant": "rs56197012",
                    "tissue_label": "macrophage",
                    "rsid": "rs56197012",
                    "molecular_trait_id": "ENSG00000008130",
                    "gene_id": "ENSG00000008130",
                    "tissue": "CL_0000235",
                    "_links": {
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000235"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012?study_accession=Nedelec_2016"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/Nedelec_2016"
                      },
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012"
                      }
                    }
                  }
                }
              },
              "_links": {
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012"
                },
                "first": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012?start=0&size=2"
                },
                "next": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/1/associations/rs56197012?start=2&size=2"
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
        :query molecular_trait_id: molecular phenotype identifier; will return only associations from this molecular phenotype (ENSG00000187583)
        :query gene_id: gene identifier; will return only associations with this gene id (ENSG00000073067)
        :query study: study identifer; will return only associations related to that study (Alasoo_2018)
        :query qtl_group: QTL group/context
        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)
        :query paginate: Flag whether the response should be paginated or not. Boolean `True` (default) or `False`

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.variants(chromosome=chromosome, variant=variant_id)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/tissues')
def get_tissues():
    """Tissues

        .. :quickref: Tissues; List all existing tissue/cell type resources

        Lists all of the existing tissue resources.

        **Example request**:

        .. sourcecode:: http

            GET /tissues HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "tissues": [
                  {
                    "_links": {
                      "associations": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000057/associations"
                      },
                      "studies": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000057/studies"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000057"
                      }
                    },
                    "tissue": "CL_0000057"
                  },
                  {
                    "_links": {
                      "associations": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000101/associations"
                      },
                      "studies": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000101/studies"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000101"
                      }
                    },
                    "tissue": "CL_0000101"
                  }
                ]
              },
              "_links": {
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues"
                },
                "first": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues?size=2&start=0"
                },
                "next": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues?size=2&start=2"
                }
              }
            }

        :query start: offset number. default is 0
        :query size: number of items returned. default is 20

        :statuscode 200: no error

    """
    resp = endpoints.tissues()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/tissues/<string:tissue>')
def get_tissue(tissue):
    """Tissue

        .. :quickref: Tissue; Lists a specific tissue/cell type ontology resource

         Lists a specific tissue/cell type resource.

        **Example request**:

        .. sourcecode:: http

            GET /tissues/CL_0000057 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_links": {
                "associations": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000057/associations"
                },
                "studies": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000057/studies"
                },
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/tissues/CL_0000057"
                }
              },
              "tissue": "CL_0000057"
            }
        
        :query start: offset number. default is 0
        :query size: number of items returned. default is 20

        :statuscode 200: no error
        :statuscode 404: not found error
    """
    resp = endpoints.tissue(tissue=tissue)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/genes')
def get_genes():
    """Genes

        .. :quickref: Genes; List all existing gene resources

        Lists all of the existing gene resources.

        **Example request**:

        .. sourcecode:: http

            GET /genes HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "gene": [
                  {
                    "gene": "ENSG00000223972",
                    "_links": {
                      "associations": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/genes/ENSG00000223972/associations"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/genes/ENSG00000223972"
                      }
                    }
                  },
                  {
                    "gene": "ENSG00000227232",
                    "_links": {
                      "associations": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/genes/ENSG00000227232/associations"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/genes/ENSG00000227232"
                      }
                    }
                  }
                ]
              },
              "_links": {
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/genes"
                },
                "first": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/genes?start=0&size=2"
                },
                "next": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/genes?start=2&size=2"
                }
              }
            }

        :query start: offset number. default is 0
        :query size: number of items returned. default is 20

        :statuscode 200: no error

    """
    resp = endpoints.genes()
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")


@api.route('/genes/<string:gene_id>')
def get_gene(gene_id):
    """Gene Resource

        .. :quickref: Gene Resource; Lists a specific gene resource.

        Lists a specific gene resource

        **Example request**:

        .. sourcecode:: http

            GET /genes/ENSG00000223972 HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "gene": "ENSG00000223972",
              "_links": {
                "associations": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/genes/ENSG00000223972/associations"
                },
                "self": {
                  "href": "http://www.ebi.ac.uk/eqtl/api/genes/ENSG00000223972"
                }
              }
            }

        :statuscode 200: no error
        :statuscode 404: not found error

    """
    resp = endpoints.gene(gene=gene_id)
    return Response(response=resp,
                    status=200,
                    mimetype="application/json")

@api.route('/genes/<string:gene_id>/associations')
def get_gene_assocs(gene_id):
    """Search Gene for Associations

        .. :quickref: Search Gene for Associations; Lists associations for a specific gene id.

        Lists associations for a specific gene id.

        **Example request**:

        .. sourcecode:: http

            GET /genes/ENSG00000070031/associations HTTP/1.1
            Host: www.ebi.ac.uk

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
              "_embedded": {
                "associations": {
                  "0": {
                    "an": 972,
                    "beta": -0.116221,
                    "median_tpm": 0.561,
                    "qtl_group": "brain",
                    "r2": 0.5648,
                    "study_id": "BrainSeq",
                    "condition": "naive",
                    "tissue_label": "brain",
                    "variant": "chr11_192658_T_C",
                    "condition_label": "naive",
                    "ref": "T",
                    "alt": "C",
                    "position": 192658,
                    "pvalue": 0.644378,
                    "maf": 0.00925926,
                    "type": "SNP",
                    "ac": 9,
                    "rsid": "rs373952992",
                    "chromosome": "11",
                    "molecular_trait_id": "ENSG00000070031",
                    "gene_id": "ENSG00000070031",
                    "tissue": "UBERON_0009834",
                    "_links": {
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/11/associations/chr11_192658_T_C"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
                      },
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/11/associations/chr11_192658_T_C?study_accession=BrainSeq"
                      }
                    }
                  },
                  "1": {
                    "an": 972,
                    "beta": -0.19745,
                    "median_tpm": 0.561,
                    "qtl_group": "brain",
                    "r2": 0.77945,
                    "study_id": "BrainSeq",
                    "condition": "naive",
                    "tissue_label": "brain",
                    "variant": "chr11_193051_G_A",
                    "condition_label": "naive",
                    "ref": "G",
                    "alt": "A",
                    "position": 193051,
                    "pvalue": 0.166599,
                    "maf": 0.0277778,
                    "type": "SNP",
                    "ac": 27,
                    "rsid": "rs144999256",
                    "chromosome": "11",
                    "molecular_trait_id": "ENSG00000070031",
                    "gene_id": "ENSG00000070031",
                    "tissue": "UBERON_0009834",
                    "_links": {
                      "variant": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/11/associations/chr11_193051_G_A"
                      },
                      "study": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/studies/BrainSeq"
                      },
                      "tissue": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/tissues/UBERON_0009834"
                      },
                      "self": {
                        "href": "http://www.ebi.ac.uk/eqtl/api/chromosomes/11/associations/chr11_193051_G_A?study_accession=BrainSeq"
                      }
                    }
                  },
               "_links": {
                "self": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/genes/ENSG00000070031/associations"
                },
                "first": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/genes/ENSG00000070031/associations?start=0&size=2"
                },
                "next": {
                  "href": "https://www.ebi.ac.uk/eqtl/api/genes/ENSG00000070031/associations?start=1&size=2"
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
        :query study: study identifer; will return only associations related to that study (Alasoo_2018)
        :query qtl_group: QTL group/context
        :query paginate: Flag whether the response should be paginated or not. Boolean `True` (default) or `False`
        :query tissue: tissue ontology identifier; will return only associations from this tissue/cell type (CL_0000235)
        :query variant_id: variant identifier, either rsID (rs577290214) or in the form CHR_BP_REF_ALT (chr7_27916_T_C); will only return associations with this variant
        :query molecular_trait_id: molecular phenotype identifier; will return only associations from this molecular phenotype (ENSG00000187583)

        :statuscode 200: no error
        :statuscode 404: not found error

    """
    resp = endpoints.gene_associations(gene=gene_id)
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
