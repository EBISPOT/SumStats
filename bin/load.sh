#!/bin/bash

# Should be run on docker container after having run setup_configuration.sh on your local machine for a specific file
# Argument is the name of the file to be loaded
# by default will take /toload and /output dirs as the location of the files to be loaded
# and the location where the output files will be saved, respectively

file=$1
study=$2
trait=$3
bp_step=$4
to_load_location=$5
config=$6

base=$(cd ${0%/*}/..; pwd)
filename=$(basename $file)
name=$(echo $filename | cut -f 1 -d '.')

gwas-load -tsv $filename -study $study -trait $trait -loader trait -config $config & pids+=($!)

for i in {1..24};
do
    chromosome_file=chr_"$i"_"$name".tsv
    if [ -s $to_load_location/$chromosome_file ];
    then
        gwas-load -tsv $chromosome_file -study $study -chr $i -loader chr -config $config & pids+=($!)
        for bp in `seq 1 $bp_step`;
        do
        bp_file=bp_"$bp"_chr_"$i"_"$name".tsv
        if [ -s $to_load_location/$bp_file ]; then
            gwas-load -tsv $bp_file -study $study -chr $i -loader snp -bp $bp -config $config & pids+=($!)
        fi
        done
    fi
done

wait "${pids[@]}"
