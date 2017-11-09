#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""

file=$1

if [ -z $file ] ;
then
    echo "$0 You need to provide the correct arguments! Exiting..."
    exit
fi
clear

 options=("variant"
        "pval"
        "chromosome"
        "or"
        "bp"
        "effect"
        "other"
        "freq"
        "beta"
        "range"
        "se")

for opt in "${options[@]}"; do

    if [ -s "$opt"_"$file" ];then
        rm "$opt"_"$file"
    fi
done

echo "Intermediate files have been deleted"

