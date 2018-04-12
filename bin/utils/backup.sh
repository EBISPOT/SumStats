#!/bin/bash

base=$(cd ${0%/*}/../..; pwd)

output_loc=$1
trait_dir=$2
chr_dir=$3
snp_dir=$4

if [ -z $output_loc ]; then
    output_loc="/output"
    echo "Setting default output location as /output ..."
fi

# backup files
cp $output_loc/$chr_dir/* $output_loc/bk_$chr_dir/ & pids+=($!)

cp -r $output_loc/$snp_dir/* $output_loc/bk_$snp_dir/ & pids+=($!)

cp $output_loc/$trait_dir/* $output_loc/bk_$trait_dir/ & pids+=($!)

wait "${pids[@]}"



