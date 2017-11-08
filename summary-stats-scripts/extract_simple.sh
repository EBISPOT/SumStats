#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""

file=$1
long_name=$2
short_name=$3

if [ -z $file ] || [ -z $long_name ] || [ -z $short_name ] ;
then
    echo "$0 You need to provide the correct arguments! Exiting..."
    exit
fi
clear
./peek.sh $file
echo -ne "Enter the $long_name ($short_name) header (NA if missing) and press [ENTER]: "
read var_header

if [ $var_header == "NA" ];then
    awk '{print "-1"}' $file > "$short_name"_"$file"
else
    ./extract_column.sh $file $var_header $short_name
fi
