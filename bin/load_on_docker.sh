#!/bin/bash

file=$1
base=$(pwd)
filename=$($base/bin/get_filename.sh $file)
study=$(echo "$file" | cut -d"-" -f2)
trait=$(echo "$file" | cut -d"-" -f3)

gwas-load -tsv $filename -study $study -trait $trait -loader trait

for i in {1..23}
do
    if [ -s /toload/chr"$i"_"$file" ];
    then
        gwas-load -tsv chr"$i"_"$file" -study $study -chr $i -loader chr
        gwas-load -tsv chr"$i"_"$file" -study $study -chr $i -loader snp
    fi
done
