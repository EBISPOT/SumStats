#!/bin/bash

base=$(cd ${0%/*}/../..; pwd)

file=$1
filename=$(basename $file)

cd $base/files/toload

for chr in {1..23}
do
    chromosome_file=chr"$chr"_"$filename"
    if [ -s $chromosome_file ];
    then
        cat $base/templates/headers $chromosome_file > temp
        mv temp $chromosome_file
    fi
done

cat $base/templates/headers $filename > temp
mv temp $filename
cd $base
