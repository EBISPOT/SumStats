#!/bin/bash

base=$(cd ${0%/*}/../..; pwd)

output_loc=$1
dir_name=$2
file=$3

cp "$output_loc"/bk_"$dir_name"/"$file" "$output_loc"/"$dir_name"/"$file"

