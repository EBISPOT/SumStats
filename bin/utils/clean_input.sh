#!/bin/bash

base=$(cd ${0%/*}/../..; pwd)

file=$1

filename=$(basename $file)
# get the first entry of the file (the snp id)
# save the ones with chr or rs id in a file called <filename>_clean
# save the ones without chr or rs id in a file called non_valid_<filename>
echo "file: $file"
echo "filename: $filename"

awk 'BEGIN{FS="\t"}{if(NR == 1){print}else{if(($1 ~ /rs/ || $1 ~ /chr/)){print}else{print $1 >> "'$base'/non_valid_'$filename'"}}}' $file > "$base"/"$filename"_clean

