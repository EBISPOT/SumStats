#!/bin/bash

base=$(cd ${0%/*}/../..; pwd)

file=$1
filename=$(basename $file)
header=$(head -n 1 $base/$filename)

cd $base/files/toload

for chr in {1..23}
do
    chromosome_file=chr"$chr"_"$filename"
    if [ -s $chromosome_file ];
    then
        echo "$header" | cat - $chromosome_file > temp
        mv temp $chromosome_file
    fi
done

echo "$header" | cat - $filename > temp
mv temp $filename
cd $base
