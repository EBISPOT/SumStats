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

You can also filter all of the association endpoints by p-value. This is done by setting either the lower p-value
threshold that you want to be cutoff, the upper p-value threshold that you want to be cutoff, or both. This is done by
passing the query parameters ``p_lower=<lower p-value>`` and/or ``p_upper=<upper p-value>`` to the API call.

Furthermore, if you would like to query associations by a base-pair location range on a specific chromosome, you can pass
in one or both of the following parameters, ``bp_lower=<lower base-pair limit>`` and ``bp_upper=<upper base-pair limit>``.
Note: base-pair location limit filtering will only work via the /chromosomes/(int: chromosome)/associations endpoint.


Requesting associations for variant
-----------------------------------

You can query the associations of a specific variant by variant id or rsid. This can be done either via the
/associations/(string: variant_id) or /associations/(string: rsid) endpoint.


Available data fields
---------------------


+-------------------------+--------+--------------------------------------------------------------+
| Name                    | Type   | Description                                                  |
+=========================+========+==============================================================+
| variant_id              | String | The variant ID (CHR_BP_REF_ALT) e.g. chr19_226776_C_T        |
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



Listing Resources
-----------------

Requests that return multiple resources will be paginated to 20 items by default. You can change number of items returned
using the size parameter.

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

It must be noted that ``next`` link offset will not always be start + size (previous offset + size of resources
returned). When filtering by p-value or by base pair location, the ``start`` query parameter in the ``next`` link will
indicate the index_marker of the database traversal. When paging through results, the next link should always be used,
and incrementing the search ``start`` parameter based on the ``size`` should be avoided.


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
| molecular_phenotyped      | Link to the molecular phenotypes resources in the database |
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
