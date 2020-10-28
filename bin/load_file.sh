#!/bin/bash


file=$1
filename=$(basename $file)
name=$(echo $filename | cut -f 1 -d '.')
study=$(echo $name | cut -d'-' -f2)
trait=$(echo $name | cut -d'-' -f3)
echo $study

min=1000
max=4000

for chr in {1..25}; do
  f=$SS_LOAD/$chr/$name.csv
  echo $f
  if [[ -f "$f" ]]; then
    chr=$(echo $f | rev | cut -f2 -d '/' | rev)
    echo $chr
    size=$(du -m $f | cut -f1)
    if (( size < min )) ; then
      mem=$(($min*3))
    elif (( size > max )) ; then
      mem=$(($size*2))
    else
      mem=$(($size*3))
    fi
    echo $mem
    bsub -o $study.out -e $study.err -M $mem -R "rusage[mem=$mem]" "gwas-load -f $filename -chr $chr -loader 'bystudy' -study $study -trait $trait"
  fi
done
