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
