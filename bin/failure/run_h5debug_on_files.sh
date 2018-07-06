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

function run_h5debug_on_dir() {
	ls $output_loc/$1 | while read line; do
		if h5debug $output_loc/$1/$line 2>&1 | grep -i -q "Error detected in HDF5" ; then
			echo "Corrupted: $1 $line"
			echo "Files corrupted"
		fi
	done
}

run_h5debug_on_dir $trait_dir

ls $output_loc/$snp_dir | while read line; do
    run_h5debug_on_dir $snp_dir/$line
done

run_h5debug_on_dir $chr_dir
