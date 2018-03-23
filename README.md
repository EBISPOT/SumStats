# SumStats

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/f6cc10c38dcc4b82a193aab3c569bb33)](https://www.codacy.com/app/olgavrou/SumStats?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/SumStats&utm_campaign=badger) [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/365f6d92792c46f3b8b446bb1151eb4c)](https://www.codacy.com/app/olgavrou/SumStats?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/SumStats&utm_campaign=Badge_Coverage)

Summary statistics with HDF5


# Installation - using Docker

Docker documentation: https://docs.docker.com

- Clone the repository
  - `git clone https://github.com/EBISPOT/SumStats.git`
  - `cd SumStats`
- Build the docker image
  - `docker build -t sumstats .`
- Run the setup script that will create the folder structure and prepare the file that you want for loading
  - python bin/preparation/setup_configuration.py -f <path to file to be processed> -config <path to json config>
- Create the container from the <sumstats> image
  - `docker run -i -p 8080:8080 -v $(pwd)/files/toload:/application/files/toload -v $(pwd)/files/output:/application/files/output -v $(pwd)/bin:/scripts -v $(pwd)/config:/application/config -t sumstats`
- Run the script to load a file on docker
  - python /scripts/preparation/load.py -f <file to be loaded> -config <path to json config> -study <study accession> -trait <efo trait>

You can run all the commands described in the secion below on the docker container that you have just launched.
 
Files produced by the sumstats package (.h5 files) should be generated in the files/output volume


# Installation - using pip install

- Clone the repository
  - `git clone https://github.com/EBISPOT/SumStats.git`
  - `cd SumStats`
- Install the sumstats package -  this will install h5py, numpy, flask, cherrypy - and sumstats
  - `pip install .`
- Run the setup script that will create the folder structure and prepare the file that you want for loading
  - python bin/preparation/setup_configuration.py -f <path to file to be processed> -config <path to json config>

# Setting properties
Under the `config` directory you will find the files that are responsible for setting the runtime properties.

`properties.py` is the default one. It can be altered but you will need to re-install the package in oreder for the changes to take effect.

`properties.json` can be edited and passed as a `-config <location to properties.json` when running: 
- `gwas-server` to run the API
- `gwas-search` to search the database via command line
- `gwas-explore` to explore what is saved in the database via command line
- `gwas-load` to load data to the database via command line

The properties that are being set are:

- h5files_path: path to the output directory where the data will be stored (see below)
- tsvfiles_path: path to the directory where the sum stats files to be loaded reside (see below)
- bp_step: how many files we want each chromosome to be split into, based on base pair location (default: 16)
- max_bp: max bp location to be found in any chromosome (default: 300,000,000)
- snp_dir: name of the directory under 'h5files_path', that the snp loader will use as to save the created h5files (default: bysnp)
- chr_dir: name of the directory under 'h5files_path', that the chromosome loader will use as to save the created h5files (default: bychr)
- trait_dir: name of the directory under 'h5files_path', that the trait loader will use as to save the created h5files (default: bytrait)
- ols_terms_location: url for querying terms in the Ontology Lookup Service API
- gwas_study_location: url for querying the study meta-data in the GWAS Catalog API
- logging_path: path to the directory where the logs will be stored
- LOG_LEVEL: log level (default is INFO)

# Default directory layout
The directories that are created are ./files/toload and ./files/output. These do not need to be named as such, and they can be located anywhere you like. You will just need to either provide the toload and output directories as arguments while running via command line, 

You can provide the preferred location by:
- passing them as arguments when running the tools via command line
- editing the config/properties.py file and re-installing the package
- editing the config/properties.json file and passing it through via command line argument

In the files/output directory 3 subdirectories will be created:
- bytrait
- bychr
- bysnp
   - dirctories named 1...22, one diractory for each chromosome

Each one will hold the hdf5 files created with the data loaded by the 3 different loaders. The loaders can be run in parallel.
Do not try and store more than one study at a time. This package does not support parallel study loading.
- loading by trait will save the data under the trait/study hdf5 group
    - a file named `file_<efo_trait>.h5` will be created, under the `bytrait` directory, one for each trait loaded, where the study groups will be stored (and the corresponding info/associations)
- loading by chromosome will save the data under the chr<chr> hdf5 group
    - a file named `file_<chromosome>.h5` will be created, under the `bychr` directory, one for each chromosome, where bp block groups that blong to this chromosome will be stored (and the corresponding info/associations)
- loading by snp will save the data under the snp<rsid> hdf5 group
    - a file named `file_<bp_step>.h5` will be created, under the `bysnp` directory, one for each chromosome, where the variant groups that belong to this chromosome will be stored (and the corresponding info/associations)

In the configuration file we have set the max bp location and the bp step that we want. Each study is split into chromosomes. Each chromosome sub-set is further split up into <bp_step> pieces based on the range, so bp 0 to max_bp with step bp_range, where bp_range = max_bp / bp_step.

So we loop through the chromosome for (default) 16 ranges of base pair locations, and create separate files for each chromosome. They are then loaded in the corresponding bysnp/<chr>/file_<bp_step>.h5 file.

# Loading
Once the package is installed you can load studies and search for studies using the command line toolkit

To load a study it is suggested that you first run the bin/setup_configuration.sh <to_load_filename> script on the file. This script will copy the file into the files/toload directory, and will split the study up into chromosomes, creating as many files as the chromosomes represented in the study. They will be named chr<x>_filename.

You can then run the below commands to fully load the study in all the formats:
1. `gwas-load -tsv chr<x>_<filename> -study <study> -chr <x> -loader chr`
2. `gwas-load -tsv chr<x>_<filename> -study <study> -chr <x> -loader snp`
3. `gwas-load -tsv <filename> -study <study> -trait <trait> -loader trait`

Assumtion: 

The script will assume that the tsv file is stored under `./files/toload` and that the output direcories will be found under the `./files/output` directory (when mounted to docker as shown above, the volumes are placed in those positions) 

If you need to specify the location where it resides, modify the properties.json file and use the `-config <path to properties.json>` flag to specify it.
   
Note that the loading command for chr and snp loaders need to be run for all the available chromosomes in the study.

# Exploring
To explore the contents of the database you can use the following commands:
- `gwas-explore -traits` will list the available traits
- `gwas-explore -studies` will list all the available studies and their corresponding traits 
- `gwas-explore -study <study>` will list the study name and it's corresponding trait

Note that, if the `output` directory is set by default to `./files/output` in the properties file. If you need to specify the location where it resides, modify the properties.json file and use the `-config <path to properties.json>` flag to specify it.

# Searching
To actually retrieve data from the database you can use the following commands:
- `gwas-search -all` will retrieve all the data from all the studies that are stored
- `gwas-search -trait <trait>` will retrieve all the data for that trait
- `gwas-search -trait <trait> -study <study>` will retrieve all the data for that trait/study combination
- `gwas-search -study <study>` will retrieve all the data for that study
- `gwas-search -chr <chr>` will retrieve all the data for that specific chromosome
- `gwas-search -snp <rsid>` will retrieve all the data for that specific snp
- `gwas-search -snp <rsid> -chr <chr>` will retrieve all the data for that specific snp and it will search for it under the chromosome given

The data will by default be retrieved in batches of 20 snps and their info per query. You can loop through the data using the default size of 20 and updating the start flag as you go: `-start <start>`, or use the flags `-start <start> -size <size>` to specify the bandwith of your retrieval.

There are two more flags that you can use:
1. `-bp floor:ceil` e.g. `-bp 10000:20000000` that specifies the range of the base pair location in the chromosome that you want. Makes sense to use when querying for a chromosome, or a trait/study
2. `-pval floor:ceil` e.g. `-pval 2e-10:5e-5` or `-pval 0.000003:4e-3` that specifies the p-value range of the results. 

Note that, if the `output` directory is set by default to `./files/output` in the properties file. If you need to specify the location where it resides, modify the properties.json file and use the `-config <path to properties.json>` flag to specify it.

# Exposing the API
To expose the API you need to run: `gwas-server`

You can use the flag `-config <path to properties.json file` to change the default properties, such as the directory where all the data is stored (output directory) as explained in all the above sections.

This will spin up the service and make it available on port 8080 (if running via docker, we exposed the port when we spinned up the container).

You should be able to see the API on http://localhost:8080/
