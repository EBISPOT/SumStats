#!/bin/bash

base=$(cd ${0%/*}/../..; pwd)

output_loc=$1

if [ -z $output_loc ]; then
    output_loc="/output"
    echo "Setting default output location as /output ..."
fi

# backup files
cp $output_loc/bychr/* $output_loc/bk_bychr/ & pids+=($!)
for chr in {1..23}
do
    cp $output_loc/bysnp/file_"$chr".h5 $output_loc/bk_bysnp/ & pids+=($!)
done
cp $output_loc/bytrait/* $output_loc/bk_bytrait/ & pids+=($!)

wait "${pids[@]}"



