#!/bin/bash

file=$1
base=$(pwd);
cd $base/files/toload

for chr in {1..23}
do
    awk 'BEGIN{FS="\t"}{if($3 == '$chr'){print;}}' $file > "chr"$chr"_"$file
done
cd $base
