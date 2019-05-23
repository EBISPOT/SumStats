#!/bin/bash

config="$EQSS_CONFIG"
base=$(cd ${0%/*}/../..; pwd)

output_loc=$1
dir_name=$2
file=$3

latest_snapshot_output=$(grep latest_snapshot_output_path $config | cut -d":" -f2 | sed 's/\"//g; s/,//g; s/ //g')

rsync -av "$latest_snapshot_output"/"$dir_name"/"$file" "$output_loc"/"$dir_name"/"$file"

