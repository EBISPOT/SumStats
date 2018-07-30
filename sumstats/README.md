# Developer documentation

This is a guide on how the code is structured and some general guidelines.

The `test` directory should mirror the sumstats directory as much as possible.

The scripts in the `bin` directory are for loading files into the database. These can be a good indicator and guide as to how
the files should be split up and which components of the code base you need to use to load files.

The `config` directory has the config module that is build with the software, and the json property file that can be passed as an
environmental variable (see main README for more details).

## Higher level components

You should use these higher level components when you want to (1) search the database (2) load data into the database (3) explore traits and studies
available in the database.

- **explorer.py**: when wanting to list all traits or all studies in the database (even from other lower level components) or look for a study in a trait
you should try and use the explorer.py class. The main reason is that it will return the lists in a sorted order.

- **load.py**: when wanting to load data into the database, this is the module you should use as an entrypoint to the database.

- **controller.py**: when wanting to query the database for associations, this is the class you should use/develop further. It should be the main
entrypoint to association search. You can query for the associations of (each query can be filtered by p-value threshold):
  - a specific trait
  - a specific study
  - a specific chromosome
  - a specific chromosome and filter by base pair location
  - a specific variant by variant id (rsid)
  - all associations

- **common_constants.py**: holds all the column header names, each column type (str, int, float, etc) and common constants that are used
throughout the code base.

## trait/chr/snp modules

These modules are used to load data by trait/ by chromosome / by variant id (snp). Each one has it's own functionality but they are all
structured in the same way.

- **constants.py**: adjust the constants defined in `common_constants.py` to apply to each modules loading/querying model
- **loader.py**: uses the `fileload.py` and `group.py` modules from sumstats.utils to parse the tsv file and load the data with the correct structure
into the database
- **retriever.py**: entrypoint into the module search/lets you know what queries are available for each storage option.
You should use this when querying data for each specific storage option. Uses the utilities named `*_search.py` under the `search` module.
- **search**: has `*_search.py` scripts that hold the `Search` classes, one for each query type we can perform.
The `Search` class uses the utilities available in the `access` module to perform the query.
The `Search` class therefore uses the `*_service.py` scripts from the `access` module to create the `Service` object (different ones for each query type).
**The `Search` object when created is passed as the `search_obj` in the general search performed by `search.py` from sumstats.utils (see the `utils module` below)
and the general search will invoke the `Service` object registered in the `Search` object which will perform the query**. The `Service` object
(called via the general_search method of the `search.py` script) applies the queries using the `repository.py` that is available under `access` to retrieve the data.
It also applies retstirctions to them and holds other useful information about the datasets and groups used. The `repository.py` module does all the heavy work, actually
traversing and returning the data in the correct format and performing checks.

To summarise the above:

1. `retriever.py` creates and calls `Search` object.
2. `Search` object creates `Service` object.
3. `Service` object uses methods in `repository.py` to access the actual data.

1. `Search` object passes self as `serach_obj` to `general_search` method of `search.py` module.
2. `Search` calls `general_search` method.
3. `general_search` method uses the search service to query the repository and apply restrictions to the data before returning the results.

## server module

This module implements the API written in Flask and let's a WSGI server launch the application (gunicorn).

- **app.py**: has all the API endpoints that are exposed to the user. It performs all the calls to the backend using the `controller.py` and the `explorer.py` higher
level modules as entrypoints as described in an above section. It uses the `api_utils.py` methods to help it construct the responses of the API endpoints.
- **api_utils.py**: a collection of methods that are used to parse the API request sent by the user and create the JSON response that will be returned to the user and other
utility mehtods that are used by `app.py`, like setting properties.
- **error_classes.py**: errors and their status codes returned by the API.

## errors module

This module is where all the Error Classes for the code base (not the ones used in the server module for the API) are defined.

## utils module

This has a lot of scripts that are used throught the codebase. Most important described here.

- **dataset.py**: utilities for datasets: each list of data to be loaded to the database or returned from the database should be wrapped in a Dataset object.
- **group.py**: utilities for groups: for creation or use of any HDF5 group, it should should be wrapped in a Group object in order for it to deal with order,
exceptions, check for None, etc. Querying, creating and expanding a Dataset under a Group should be done via this wrapper object.
- **properties_handler.py**: responsible for setting/getting external properties needed/if the SS_CONFIG enviromental variable is not empty it sets the new properties.
- **register_logger.py**: when a new class/module is created you can register it's logger via this module
- **search.py**: is the general search method used by all the '*_search.py' modules in the trait/chr/snp modules