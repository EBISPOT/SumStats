#!/bin/bash

file=$1
base=$(pwd);
cd $base/files/toload

for chr in {1..23}
do
    chromosome_file=chr"$chr"_"$file"
    if [ -s $chromosome_file ];
    then
        cat $base/templates/headers $chromosome_file > temp
        mv temp $chromosome_file
    fi
done

cat $base/templates/headers $file > temp
mv temp $file
cd $base
