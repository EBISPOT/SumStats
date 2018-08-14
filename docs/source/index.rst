.. sumstats documentation master file, created by
   sphinx-quickstart on Fri Aug 10 12:09:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. contents:: The Summary Statistics Database API Documentation

API quick reference
===================

.. qrefflask:: sumstats.server.app:app
   :undoc-static:
   :order: path


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

+---------------------+------------------------------------+
| Status code         | Usage                              |
+=====================+====================================+
| ``200 OK``          | The request completed successfully |
+---------------------+------------------------------------+
| ``400 Bad Request`` | The request completed successfully |
+---------------------+------------------------------------+
| ``404 Not Found``   | The request completed successfully |
+---------------------+------------------------------------+

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
Application Language (HAL) format. Links can be found benath the _links key. Users of the API should not created URIs
themselves, instead they should use the above-described links to navigate from resource to resource.


API General Guidelines
======================

Association Queries
-------------------

For all endpoints that return associations you can assume the below.

Default data values displayed are the harmonised values. You can query specifically for the original or 'raw' values of
the data or you can query for both harmonised and raw values to be displayed. Harmonised values will, in the latter case,
be prefixed with ``hm_``. This is done by passing the query parameter ``reveal=raw`` or ``reveal=all`` in the API call.

You can also filter all of the association endpoints by p-value. This is done by setting either the lower p-value
threshold that you want to be cutoff, the upper p-value threshold that you want to be cutoff, or both. This is done by
passing the query parameters ``p_lower=<lower p-value>`` and/or ``p_upper=<upper p-value>`` to the API call.


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
         "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations"
       },
       "first": {
         "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations?size=1&start=0"
       },
       "next": {
         "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations?size=1&start=1"
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
         "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/associations"
       },
       "traits": {
         "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/traits"
       },
       "studies": {
         "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/studies"
       },
       "chromosomes": {
         "href": "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes"
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

+--------------+---------------------------------------------------+
| Relation     | Description                                       |
+==============+===================================================+
| associations | Link to the association resources in the database |
+--------------+---------------------------------------------------+
| traits       | Link to the trait resources in the database       |
+--------------+---------------------------------------------------+
| studies      | Link to the study resources in the database       |
+--------------+---------------------------------------------------+
| chromosomes  | Link to the chromosome resources in the database  |
+--------------+---------------------------------------------------+


API detailed reference
======================

.. autoflask:: sumstats.server.app:app
   :undoc-static:
   :order: path