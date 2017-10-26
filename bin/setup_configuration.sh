#!/bin/bash

# Run from parent directory
# Input: the file that will be loaded (columns should conform in
# sequence with the templates/headers file)
# Will:
# (a) clean up the file from non-valid variant IDs
# (b) append the postfix "_loaded" to the input file
# (c) move the clean input file to the <parent>/files/toload directory
# (d) create up to 23 sub files named chr<x>_<filename> in the
#       <parent>/files/toload directory each file containing the information
#       for its correspoding chromosome
# (e) append the same header to all the eligible files to be loaded
# (f) create a config file in the <parent> directory, one for
#       the file, and one for each subfile to be loaded


file=$1
base=$(pwd);
echo "base: $base"
filename=$($base/bin/get_filename.sh $file)


# takes the file given as input and creates a clean one with "_clean" appended to it
echo "FILE: $file"
$base/bin/clean_input.sh "$file"
# move it to the correct location
mv "$file" "$file"_loaded
mv "$file"_clean $base/files/toload/"$file"

# split up the script into one per chromosome
filename="$filename"
$base/bin/split_by_chr.sh "$filename"
$base/bin/append_header.sh "$filename"

$base/bin/create_chr_configuration.sh $filename
$base/bin/create_trait_configuration.sh $filename
$base/bin/create_snp_configuration.sh $filename
