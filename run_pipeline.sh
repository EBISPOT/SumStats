#!/bin/bash
source activate sumstats #activate conda env

bsub -q production-rh74 "snakemake 2> snakemake.err -w 60 --configfile $SS_CONFIG -j 1000 --rerun-incomplete --keep-going --cluster 'bsub -M {params.mem} -R \"rusage[mem={params.mem}]\" -oo stdin.txt -eo stderr -q production-rh74 -g /sumstats'; mail -s \"snakemake finished\" jhayhurst@ebi.ac.uk < snakemake.err"

source deactivate
