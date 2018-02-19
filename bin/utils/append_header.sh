#!/bin/bash

base=$(cd ${0%/*}/../..; pwd)

file=$1
header=$2
filename=$(basename $file)

cd $base/files/toload

for chr in {1..23}
do
    chromosome_file=chr"$chr"_"$filename"
    if [ -s $chromosome_file ];
    then
        echo "$2" | cat - $chromosome_file > temp
        mv temp $chromosome_file
    fi
done

echo "$2" | cat - $filename > temp
mv temp $filename
cd $base
