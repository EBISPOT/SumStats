#!/bin/bash

file=$1
base=$(pwd);

filename=$($base/bin/get_filename.sh $file)
# get the first entry of the file (the snp id)
# save the ones with chr or rs id in a file called <filename>_clean
# save the ones without chr or rs id in a file called non_valid_<filename>
echo "file: $file"
echo "filename: $filename"

awk 'BEGIN{FS="\t"}{if(($1 ~ /rs/ || $1 ~ /chr/) && !($0 ~ /NA/ || $0 ~ /na/)){print}else{print $1 >> "non_valid_'$filename'"}}' $file > "$filename"_clean

