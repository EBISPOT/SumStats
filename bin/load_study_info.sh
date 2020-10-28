#!/bin/bash


file=$1
filename=$(basename $file)
name=$(echo $filename | cut -f 1 -d '.')
study=$(echo $name | cut -d'-' -f2)
trait=$(echo $name | cut -d'-' -f3)
echo $study

gwas-load -f $filename -loader 'study_info' -study $study -trait $trait
