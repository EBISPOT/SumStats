#!/bin/bash

# Input: the file that will be loaded (columns should conform in
# sequence with the templates/headers file)
# Will:
# (a) clean up the file from non-valid variant IDs
# (b) move the clean input file to the <parent>/files/toload directory
# (c) create up to 23 sub files named chr<x>_<filename> in the
#       <parent>/files/toload directory each file containing the information
#       for its correspoding chromosome
# (d) append the same header to all the eligible files to be loaded

base=$(cd ${0%/*}/..; pwd)

file=$1
filename=$(basename $file)

# create input and output directories if they don't exist
mkdir -p $base/files/toload
mkdir -p $base/files/output/bychr
mkdir -p $base/files/output/bytrait
mkdir -p $base/files/output/bysnp

# takes the file given as input and creates a clean one with "_clean" appended to it
echo "FILE: $file"
header=$(head -n 1 $base/$filename)
$base/bin/utils/clean_input.sh "$base/$filename"
# move it to the correct location
mv $base/"$filename"_clean $base/files/toload/"$filename"

# split up the script into one per chromosome

$base/bin/utils/split_by_chr.sh "$filename"
$base/bin/utils/append_header.sh "$filename" "$header"

