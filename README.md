# SumStats

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/f6cc10c38dcc4b82a193aab3c569bb33)](https://www.codacy.com/app/olgavrou/SumStats?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/SumStats&utm_campaign=badger)

[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/365f6d92792c46f3b8b446bb1151eb4c)](https://www.codacy.com/app/olgavrou/SumStats?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/SumStats&utm_campaign=Badge_Coverage)

Summary statistics with HDF5


# Installation - using Docker

Docker documentation: https://docs.docker.com

- Clone the repository
  - `git clone https://github.com/EBISPOT/SumStats.git`
  - `cd SumStats`
- Build the docker image
  - `docker build -t sumstats`
- Run the setup script that will create the folder structure and prepare the file that you want for loading
  - bin/setup_configuration.sh <to_load_filename>
- Create the container from the <sumstats> image
  - `docker run -i -v $(pwd)/files/toload:/toload -v $(pwd)/files/output:/output -v $(pwd)/bin:/scripts -t sumstats`
- Run the script to load a file on docker
  - load_on_docker.sh <to_load_filename>
 
Files produced by the sumstats package (.h5 files) should be generated in the files/output volume


# Installation - using pip install

- Clone the repository
  - `git clone https://github.com/EBISPOT/SumStats.git`
  - `cd SumStats`
- Install the sumstats package -  this will install h5py, numpy, flask, cherrypy - and sumstats
  - `pip install .`
- Run the setup script that will create the folder structure and prepare the file that you want for loading
  - bin/setup_configuration.sh <to_load_filename>
  
# Directory layout
The directories that are created are files/toload and files/output
In the files/output directory 3 subdirectories will be created:
- bytrait
- bychr
- bysnp

Each one will hold the hdf5 files created with the data loaded by the 3 different loaders. The loaders can be run in parallel.
Do not try and store more than one study at a time. This package does not support parallel study loading.
- loading by trait will save the data under the trait/study hdf5 group
- loading by chromosome will save the data under the chr<chr> hdf5 group
- loading by snp will save the data under the snp<rsid> hdf5 group

# Loading
Once the package is installed you can load studies and search for studies using the command line toolkit

To load a study it is suggested that you first run the bin/setup_configuration.sh <to_load_filename> script on the file. This script will copy the file into the files/toload directory, and will split the study up into chromosomes, creating as many files as the chromosomes represented in the study. They will be named chr<x>_filename.

You can then run the below commands to fully load the study in all the formats:
1. `gwas-load -tsv chr<x>_<filename> -study <study> -chr <x> -loader chr`
    - the script will assume that the tsv file is stored under `/toload` and that the output direcories will be found under the `/output` directory (when mounted to docker as shown above, the volumes are placed in those positions) 
    - if the `toload` directory and the `output` directory are located somewhere else you need to specify it when running the gwas-load command using the `-input_path <path to where the /toload dir is located> -output_path <path to where the /output dir is located>` flags
2. `gwas-load -tsv chr<x>_<filename> -study <study> -chr <x> -loader snp`
    - consider the same assuptions as above
3. `gwas-load -tsv <filename> -study <study> -trait <trait> -loader trait`
    - consider the same assuptions as above
   
Note that the loading command for chr and snp loaders need to be run for all the available chromosomes in the study.

# Exploring
To explore the contents of the database you can use the following commands:
- `gwas-explore -traits` will list the available traits
- `gwas-explore -studies` will list all the available studies and their corresponding traits 
- `gwas-explore -study <study>` will list the study name and it's corresponding trait

Note that, again, if the `/output` directory is not under root, i.e. `/output`, the you need to specify the location where it resides using the `path <path to where the /output dir is located>` flag.

# Searching
To actually retrieve data from the database you can use the following commands:
- `gwas-search -all` will retrieve all the data from all the studies that are stored
- `gwas-search -trait <trait>` will retrieve all the data for that trait
- `gwas-search -trait <trait> -study <study>` will retrieve all the data for that trait/study combination
- `gwas-search -chr <chr>` will retrieve all the data for that specific chromosome
- `gwas-search -snp <rsid>` will retrieve all the data for that specific snp

The data will by default be retrieved in batches of 20 snps and their info per query. You can loop through the data using the default size of 20 and updating the start flag as you go: `-start <start>`, or use the flags `-start <start> -size <size>` to specify the bandwith of your retrieval.

There are two more flags that you can use:
1. `-bp floor:ceil` e.g. `-bp 10000:20000000` that specifies the range of the base pair location in the chromosome that you want. Makes sense to use when querying for a chromosome, or a trait/study
2. `-pval floor:ceil` e.g. `-pval 2e-10:5e-5` or `-pval 0.000003:4e-3` that specifies the p-value range of the results. 

Note that, again, if the `/output` directory is not under root, i.e. `/output`, the you need to specify the location where it resides using the `path <path to where the /output dir is located>` flag.
