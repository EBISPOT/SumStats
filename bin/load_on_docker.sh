#!/bin/bash

# Should be run on docker container after having run setup_configuration.sh on your local machine for a specific file
# Argument is the name of the file to be loaded
# by default will take /toload and /output dirs as the location of the files to be loaded
# and the location where the output files will be saved, respectively


file=$1
base=$(cd ${0%/*}/..; pwd)

filename=$(basename $file)
study=$(echo "$filename" | cut -d"-" -f2)
trait=$(echo "$filename" | cut -d"-" -f3)

gwas-load -tsv $filename -study $study -trait $trait -loader trait

for i in {1..23}
do
    if [ -s /toload/chr"$i"_"$filename" ];
    then
        gwas-load -tsv chr"$i"_"$filename" -study $study -chr $i -loader chr
        gwas-load -tsv chr"$i"_"$filename" -study $study -chr $i -loader snp
    fi
done
