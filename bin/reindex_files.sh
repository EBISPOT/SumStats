#!/bin/bash

f=$1
name=$(basename $f | sed 's/.tsv//')
for i in {1..25}; do
  h5file=$SS_OUT/bystudy/$i/file_$name.h5
  if [[ -f $h5file ]]; then
    echo "reindexing $h5file"
    gwas-reindex -f $h5file
  else
    echo "Unable to reindex $h5file"
  fi
done
