#!/bin/bash

base=$(cd ${0%/*}/../..; pwd)

output_loc=$1

if [ -z $output_loc ]; then
    output_loc="/output"
    echo "Setting default output location as /output ..."
fi

function run_h5debug_on_dir() {
	ls $output_loc/$1 | while read line; do
		if h5debug /output/$1/$line 2>&1 | grep -i -q "Error detected in HDF5" ; then
			/scripts/utils/rollback.sh "/output" $1 $line
			echo "Rolled back: $1 $line"
		fi
	done
}

run_h5debug_on_dir bychr
run_h5debug_on_dir bysnp
run_h5debug_on_dir bytrait
