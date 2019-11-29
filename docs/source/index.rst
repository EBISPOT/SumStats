.. sumstats documentation master file, created by
   sphinx-quickstart on Fri Aug 10 12:09:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. .. contents:: The eQTL Catalogue Summary Statistics API Documentation

eQTL Catalogue Summary Statistics API Documentation
===================================================


Overview
========


HTTP Verbs
----------

This API supports the following HTTP verbs.

+---------+-----------------------------+
| Verb    | Usage                       |
+=========+=============================+
| ``GET`` | Used to retrieve a resource |
+---------+-----------------------------+

HTTP status codes
-----------------

This API tries to adhere as closely as possible to standard HTTP and REST conventions in its use of HTTP status codes.

+---------------------+-------------------------------------------------------------------------------------------------+
| Status code         | Usage                                                                                           |
+=====================+=================================================================================================+
| ``200 OK``          | The request completed successfully                                                              |
+---------------------+-------------------------------------------------------------------------------------------------+
| ``400 Bad Request`` | The request was malformed. The response body will include an error providing further information|
+---------------------+-------------------------------------------------------------------------------------------------+
| ``404 Not Found``   | The requested resource did not exist                                                            |
+---------------------+-------------------------------------------------------------------------------------------------+

Errors
------

Whenever an error response (status code >= 400) is returned, the body will contain a JSON object that describes the
problem. The error object has the following structure:

+------------+------------+----------------------------------------------------+
| Path       | Type       | Description                                        |
+============+============+====================================================+
| error      | String     | The HTTP error that occurred, e.g. ``Bad Request`` |
+------------+------------+----------------------------------------------------+
| message    | String     | A description of the cause of the error            |
+------------+------------+----------------------------------------------------+
| status     | Number     | The HTTP status code, e.g. ``400``                 |
+------------+------------+----------------------------------------------------+

Hypermedia
----------

This API uses hypermedia and resources include links to other resources in their responses. Responses are in Hypertext
Application Language (HAL) format. Links can be found beneath the _links key. Users of the API should not created URIs
themselves, instead they should use the above-described links to navigate from resource to resource.


API quick reference
===================

With the exception of genomic region requests, all requests for associations can all be made using the ``/associations`` endpoint, adding and combining parameters as needed for filtering. 

.. qrefflask:: sumstats.server.app:app
   :undoc-static:
   :order: path

API General Guidelines
======================

Association Queries
-------------------

For all endpoints that return associations you can assume the below.

Default data values displayed are from the 'ge' (gene counts) quantification method. You can query specifically for any 
other quantification method choosing from the table below:

===================== ============
Quantification method Reference
===================== ============
Gene counts           'ge'
Exon counts           'exon'
Microarray            'microarray'
Transcript usage      'tx'
Txrevise              'txrevise'
===================== ============

Use the reference to specify the quantification method. For instance, if you want to view exon count data use the query
parameter ``quant_method=exon``. By default ``quant_method`` is set to 'ge'. It is not possible to view all the quantification
methods in one API call. 

Depending on the endpoint, you can filter by the following parameters:

================= ==================== ======================================
Parameter         Label                Example
================= ==================== ======================================
Molecular trait   'molecular_trait_id' ``molecular_trait_id=ENSG00000187583``
Gene              'gene_id'            ``gene_id=ENSG00000073067``
Variant           'variant_id'         ``variant_id=rs577290214``
Study             'study'              ``study=Alasoo_2018``
Tissue ontology   'tissue'             ``tissue=CL_0000235``
QTL group/context 'qtl_group'          ``qtl_group=macrophage_IFNg``
================= ==================== ======================================

The above parameters can be applied to any endpoint that does not already search/filter by that parameter, e.g. the molecular trait parameter is ignored when applied to the molecular phenotypes endpoint. The parameters can be combined using the ``&`` operator to filter the data as much as needed but any single parameter can only be called once i.e. it is not possible to filter for multiple genes, for that you must make separate queries. In the case a combination of ``tissue`` and ``qtl_group``, any QTL group will supersede the tissue filter, effectively nullifying the tissue filter. This is because a QTL context refers to a tissue and condition e.g. if the tissue/cell type is 'macrophage' and the condition/treatment is 'Salmonella', the corresponding QTL group is 'macrophage_Salmonella'.

You can also filter all of the association endpoints by p-value. This is done by setting either the lower p-value
threshold that you want to be cutoff, the upper p-value threshold that you want to be cutoff, or both. This is done by
passing the query parameters ``p_lower=<lower p-value>`` and/or ``p_upper=<upper p-value>`` to the API call.

Furthermore, if you would like to query associations by a base-pair location range on a specific chromosome, you can pass
in one or both of the following parameters, ``bp_lower=<lower base-pair limit>`` and ``bp_upper=<upper base-pair limit>``.
Note: base-pair location limit filtering will only work via the /chromosomes/(int: chromosome)/associations endpoint.


Response format
---------------
The paginate parameter, ``paginate``, allows you to flag whether the response should be paginated (using the ``size`` and ``start`` parameters) or not. By default it is set to 'True', but if set to 'False' the ``size`` and ``start`` parameters are ignored and the response will contain every hit. When using the un-paginated format none of the links seen in the paginated format will be present. Note that ``paginate=False`` can only be used on sufficiently filtered payloads (to avoid transmitting huge payloads). A sufficiently filtered request adheres to the following: ``study`` & ``qtl_group`` & (``gene_id`` or ``molecular_trait_id`` or ``variant_id``) i.e. requests for genes, molecular traits or variants for a specific study and QTL group can be returned as one single payload rather than paged responses.


Requesting associations for variant
-----------------------------------

You can query the associations of a specific variant by variant id or rsID. This can be done either via the
``/associations/(string: variant_id)`` or ``/associations/(string: rsid)`` endpoint, or it can be done as a parameter query like ``/associations/?variant_id=(string: variant_id/rsid)``.


Available data fields
---------------------


+-------------------------+--------+--------------------------------------------------------------+
| Name                    | Type   | Description                                                  |
+=========================+========+==============================================================+
| variant                 | String | The variant ID (CHR_BP_REF_ALT) e.g. chr19_226776_C_T        |
+-------------------------+--------+--------------------------------------------------------------+
| rsid                    | String | The rsID, if given, for the variant                          |
+-------------------------+--------+--------------------------------------------------------------+
| chromosome              | Number | GRCh38 chromosome name of the variant                        |
+-------------------------+--------+--------------------------------------------------------------+
| position                | Number | GRCh38 position of the variant                               |
+-------------------------+--------+--------------------------------------------------------------+
| study_id                | String | The study identifier e.g. Alasoo_2018                        |
+-------------------------+--------+--------------------------------------------------------------+
| molecular_trait_id      | String | ID of the molecular trait e.g. ENSG00000156508               |
+-------------------------+--------+--------------------------------------------------------------+
| pvalue                  | Number | P-value of association between the variant and the phenotype |
+-------------------------+--------+--------------------------------------------------------------+
| ac                      | Number | Allele count                                                 |
+-------------------------+--------+--------------------------------------------------------------+
| alt                     | String | GRCh38 effect allele (alt allele)                            |
+-------------------------+--------+--------------------------------------------------------------+
| ref                     | String | GRCh38 other allele (reference allele)                       |
+-------------------------+--------+--------------------------------------------------------------+
| maf                     | Number | Minor allele frequency within the QTL mapping study          |
+-------------------------+--------+--------------------------------------------------------------+
| mean_expr               | Number | Expression value for the associated gene + qtl_group         |
+-------------------------+--------+--------------------------------------------------------------+
| type                    | String | SNP, INDEL or OTHER                                          |
+-------------------------+--------+--------------------------------------------------------------+
| an                      | Number | Total number of alleles                                      |
+-------------------------+--------+--------------------------------------------------------------+
| beta                    | Number | Regression coefficient from the linear model                 |
+-------------------------+--------+--------------------------------------------------------------+
| se                      | Number | The beta's standard error                                    |
+-------------------------+--------+--------------------------------------------------------------+
| gene_id                 | String | Ensembl gene ID                                              |
+-------------------------+--------+--------------------------------------------------------------+
| r2                      | Number | Imputation quality score from the imputation software        |
+-------------------------+--------+--------------------------------------------------------------+
| qtl_group               | String | Controlled vocabulary for the QTL group (tissue & condition) |
+-------------------------+--------+--------------------------------------------------------------+
| tissue                  | String | Ontology term for the tissue/cell type                       |
+-------------------------+--------+--------------------------------------------------------------+
| tissue_label            | String | Controlled vocabulary for the tissue/cell type               |
+-------------------------+--------+--------------------------------------------------------------+
| condition               | String | Controlled vocabulary for the condition/treatment            |
+-------------------------+--------+--------------------------------------------------------------+
| condition_label         | String | More verbose condition description                           |
+-------------------------+--------+--------------------------------------------------------------+



Listing Resources
-----------------

Requests that return multiple resources will be paginated to 20 items by default. You can change number of items returned
using the size parameter. The maximum size value is 1000 and any value given greater than 1000 will be converted to 1000.

**Paging resources**

Links will be provided in the response to navigate the resources.

*Example request*:

.. sourcecode:: http

   GET /associations?size=1 HTTP/1.1
   Host: www.ebi.ac.uk

*Example response*:

.. sourcecode:: http

   HTTP/1.1 200 OK
   Content-Type: application/json

.. code-block:: JSON

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
         }
       }  
     },
     "_links": {
       "self": {
         "href": "https://www.ebi.ac.uk/eqtl/api/associations"
       },
       "first": {
         "href": "https://www.ebi.ac.uk/eqtl/api/associations?size=1&start=0"
       },
       "next": {
         "href": "https://www.ebi.ac.uk/eqtl/api/associations?size=1&start=1"
       }
     }
   }

**Response structure**

+------------+------------+---------------------------+
| Path       | Type       | Description               |
+============+============+===========================+
| _links     | Object     | Links to other resources  |
+------------+------------+---------------------------+
| _embedded  | Object     | The list of resources     |
+------------+------------+---------------------------+

**Links**

+------------+-------------------------------------+
| Relation   | Description                         |
+============+=====================================+
| self       | This resource list                  |
+------------+-------------------------------------+
| first      | The first page in the resource list |
+------------+-------------------------------------+
| next       | The next page in the resource list  |
+------------+-------------------------------------+

When paging through results, the next link should always be used,
and incrementing the search ``start`` parameter based on the ``size`` should be avoided. 
If you would like to return an un-paginated payload containing all the results, see :ref:`Response format`.

Accessing the API
=================

The api endpoint provides the entry point into the service.

A ``GET`` request is used to access the API.

**Example request**:

.. sourcecode:: http

   GET / HTTP/1.1
   Host: www.ebi.ac.uk

**Example response**:

.. sourcecode:: http

   HTTP/1.1 200 OK
   Content-Type: application/json

.. code-block:: JSON

   {
     "_links": {
       "associations": {
             "href": "https://www.ebi.ac.uk/eqtl/api/associations"
       },
       "molecular_phenotypes": {
             "href": "https://www.ebi.ac.uk/eqtl/api/molecular_phenotypes"
       },
       "studies": {
             "href": "https://www.ebi.ac.uk/eqtl/api/studies"
       },
       "tissues": {
             "href": "https://www.ebi.ac.uk/eqtl/api/tissues"
       },
       "genes": {
             "href": "https://www.ebi.ac.uk/eqtl/api/genes"
       },
       "chromosomes": {
             "href": "https://www.ebi.ac.uk/eqtl/api/chromosomes"
       }
     }
   }



**Response structure**

+------------+------------+---------------------------+
| Path       | Type       | Description               |
+============+============+===========================+
| _links     | Object     | Links to other resources  |
+------------+------------+---------------------------+

**Links**

+---------------------------+------------------------------------------------------------+
| Relation                  | Description                                                |
+===========================+============================================================+
| associations              | Link to the association resources in the database          |
+---------------------------+------------------------------------------------------------+
| molecular_phenotypes      | Link to the molecular phenotypes resources in the database |
+---------------------------+------------------------------------------------------------+
| studies                   | Link to the study resources in the database                |
+---------------------------+------------------------------------------------------------+
| tissues                   | Link to the tissue resources in the database               |
+---------------------------+------------------------------------------------------------+
| genes                     | Link to the gene resources in the database                 |
+---------------------------+------------------------------------------------------------+
| chromosomes               | Link to the chromosome resources in the database           |
+---------------------------+------------------------------------------------------------+


API detailed reference
======================

.. autoflask:: sumstats.server.app:app
   :undoc-static:
   :order: path
