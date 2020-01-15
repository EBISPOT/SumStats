# eQTL Summary Statistics

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/01c24035b9634ad1aaa7f66598be2483)](https://www.codacy.com/app/spot-ebi/SumStats?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=EBISPOT/SumStats&amp;utm_campaign=Badge_Grade) [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/01c24035b9634ad1aaa7f66598be2483)](https://www.codacy.com/app/spot-ebi/SumStats?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/SumStats&utm_campaign=Badge_Coverage)

EQTL Summary statistics with HDF5

The concept is to leverage the fast query times and multidimensional indexing capabilities of HDF5 to enable fast, useful querying of very large summary statistics datasets. There are loading scripts to convert TSV summary statistics to HDF5 using [PyTables](https://www.pytables.org/). Command line utilities enable the querying of HDF5, and a Python Flask app to serves the data via a REST API. This is conterised and deployed to the cloud using Kubernetes.


# Local installation - using conda and pip

- Clone the repository
  - `git clone https://github.com/EBISPOT/SumStats.git`
  - `cd SumStats`
- Create conda environment (installs HDF5 lib and other dependencies)
	- `conda env create -f sumstats.yml`
	- `conda  activate  sumstats`
- pip install the sumstats package -  this will install pytables, numpy, flask, gunicorn - and sumstats
  - `pip install -r requirements.txt`
  - `pip install .`


# Setting properties
Under the `config` directory you will find the files that are responsible for setting the runtime properties.

`properties.py` is the default one. It can be altered but you will need to re-install the package in oreder for the changes to take effect.

`properties.json` can be edited and passed as a an environmental variable as: `export EQSS_CONFIG=<path to json config>` when running:
- `gunicorn -b <host:port> --chdir sumstats/server --access-logfile <path to access log file> --error-logfile <path to error log file> app:app [--log-level <log level>]` to run the API
- `eqtl-search` to search the database via command line
- `eqtl-explore` to explore what is saved in the database via command line


# Loading

Data loading means converting tsv data to HDF5. It involves merging in data from FIVE sources - i) summary statistics, ii) variant data, iii) expression data, iv) phenotype metadata, v) rsids from dbsnp. These data are split and joined to produce CSV and HDF5 files, where each file represents a study X qtl group X tissue X chromosome.
Once the package is installed you can load studies and search for studies using the command line toolkit.

```
$ eqtl-load --help
usage: eqtl-load [-h] [-f F] [-csv CSV] [-var VAR] [-phen PHEN] [-expr EXPR]
                 [-study STUDY] [-qtl_group QTL_GROUP] [-quant QUANT]
                 [-tissue TISSUE] [-chr CHR] -loader {study,trait,study_info}
                 [-tissue_ont TISSUE_ONT] [-treatment TREATMENT]
                 [-treatment_ont TREATMENT_ONT]

optional arguments:
  -h, --help            show this help message and exit
  -f F                  The path to the summary statistics file to be
                        processed
  -csv CSV              The path to the csv OUT file
  -var VAR              The path to the variant/genotype metadata file
  -phen PHEN            The path to the trait/phenotype metadata file
  -expr EXPR            The path to the gene expression file
  -study STUDY          The study identifier
  -qtl_group QTL_GROUP  The qtl group e.g. "LCL"
  -quant QUANT          The quantification method e.g. "gene counts"
  -tissue TISSUE        The tissue
  -chr CHR              The chromosome the data belongs to
  -loader {study,trait,study_info}
                        The loader
  -tissue_ont TISSUE_ONT
                        The tissue ontology term
  -treatment TREATMENT  The treatment
  -treatment_ont TREATMENT_ONT
                        The treatment ontology term
```

After conversion to HDF5, the file should be indexed (the fields to index can be modified in the [common_constants.py](sumstats/common_constants.py) file):

```
$ eqtl-reindex --help
usage: eqtl-reindex [-h] -f F

optional arguments:
  -h, --help  show this help message and exit
  -f F        The path to the HDF5 file to be processed
```

It is recommended to 'repack' the HDF5 to save disk space. Utilise the PyTables [`ptrepack`](https://www.pytables.org/usersguide/utilities.html#ptrepack) command line utility 


# Exploring
To explore the contents of the database you can use the following commands:

```
$ eqtl-explore --help
usage: eqtl-explore [-h] [-molecular_phenotypes]
                    [-molecular_phenotype MOLECULAR_PHENOTYPE] [-studies]
                    [-study STUDY] [-tissues] [-tissue TISSUE] [-chromosomes]
                    [-genes]

optional arguments:
  -h, --help            show this help message and exit
  -molecular_phenotypes
                        List all the molecular_phenotypes
  -molecular_phenotype MOLECULAR_PHENOTYPE
                        List all the studies for a molecular_phenotype
  -studies              List all the studies
  -study STUDY          Will list 'trait: study' if it exists
  -tissues              List all the tissues
  -tissue TISSUE        Will list 'study: tissue' if it exists
  -chromosomes          Will list all the chromosomes
  -genes                List all the genes
```


# Searching 
To retrieve data from the database you can use the following commands:
```
$ eqtl-search --help
usage: eqtl-search [-h] [-path PATH] [-all] [-start START] [-size SIZE]
                   [-trait TRAIT] [-gene GENE] [-study STUDY] [-tissue TISSUE]
                   [-qtl_group QTL_GROUP] [-snp SNP] [-chr CHR] [-pval PVAL]
                   [-bp BP] [-quant_method {ge,tx,txrev,microarray,exon}]
                   [-paginate [PAGINATE]]

optional arguments:
  -h, --help            show this help message and exit
  -path PATH            Full path to the dir where the h5files will be stored
  -all                  Use argument if you want to search for all
                        associations
  -start START          Index of the first association retrieved
  -size SIZE            Number of retrieved associations
  -trait TRAIT          The trait I am looking for
  -gene GENE            The gene I am looking for
  -study STUDY          The study I am looking for
  -tissue TISSUE        The tissue I am looking for
  -qtl_group QTL_GROUP  The QTL group/context I am looking for
  -snp SNP              The SNP I am looking for
  -chr CHR              The chromosome I am looking for
  -pval PVAL            Filter by pval threshold: -pval floor:ceil
  -bp BP                Filter with baise pair location threshold: -bp
                        floor:ceil
  -quant_method {ge,tx,txrev,microarray,exon}
                        The quantification method
  -paginate [PAGINATE]  Sets paginate to "False" if you would like to fetch
                        all associations for your query
```
The data will by default be retrieved in batches of 20 snps and their info per query. You can loop through the data using the default size of 20 and updating the start flag as you go: `-start <start>`, or use the flags `-start <start> -size <size>` to specify the bandwith of your retrieval. The default value of `quant_method` is 'ge'. F

There are two more flags that you can use:
1. `-bp floor:ceil` e.g. `-bp 10000:20000000` that specifies the range of the base pair location in the chromosome that you want. Makes sense to use when querying for a chromosome, or a trait/study
2. `-pval floor:ceil` e.g. `-pval 2e-10:5e-5` or `-pval 0.000003:4e-3` that specifies the p-value range of the results. 

Note that, if the `output` directory is set by default to `./files/output` in the properties file. If you need to specify the location where it resides, modify the properties.json file and set `export EQSS_CONFIG=<path to json config>`  accordingly.

The API uses the same search module and is more thoroughly documented [here](https://www.ebi.ac.uk/eqtl/api-docs/), which will explain the fields and constraints.

# Exposing the API
To expose the API you need to run: `gunicorn -b <host:port> --chdir sumstats/server --access-logfile <path to access log file> --error-logfile <path to error log file> app:app [--log-level <log level>]`

You can set the environmental variable as: `export EQSS_CONFIG=<path to json config>` to change the default properties, such as the directory where all the data is stored (output directory) as explained in all the above sections.

This will spin up the service and make it available on port 8080 (if running via docker, we exposed the port when we spinned up the container).

You should be able to see the API on http://localhost:8080/

# Deployment
Kubernetes delpoyment has been configured with gitlab using [.gitlab-ci.yml](.gitlab-ci.yml) and [helm](eqtlss).
