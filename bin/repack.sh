#!/bin/bash

file=$1
chrom=$2
filename=$(basename $file)
name=$(echo $filename | cut -f 1 -d '.')
study=$(echo $name | cut -d'-' -f2)
trait=$(echo $name | cut -d'-' -f3)
h5file=$SS_OUT/bystudy/$chrom/file_$name.h5
if [[ -f $h5file ]]; then
  echo $h5file
  echo $SS_OUT/bychr/file_chr$chrom.h5:/$study
  ptrepack -v --complib blosc:snappy --complevel 9 --overwrite-nodes --chunkshape 'auto' --sortby 'base_pair_location' --propindexes $h5file:/$study $SS_OUT/bychr/file_chr$chrom.h5:/$study
else
  echo "no file $h5file to repack"
fi
