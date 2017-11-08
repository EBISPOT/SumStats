#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""

file=$1

if [ -z $file ];
then
    echo -e "${RED}You need to run the script with the file name as a parameter"
    echo -e "${RED}Example: menu.sh sum-stats-file.csv"
    echo -e "${NC}"
    exit
fi
clear
./peek.sh $file
echo -ne "Enter the header name of the chromosome and press [ENTER]: "
read var_header

echo -ne "Enter the prefix of the chromosome (if any) and press [ENTER], OR just press [ENTER]: "
read prefix

if [ -n $prefix ];then

    ./extract_column.sh $file $var_header chromosome
    while read line; do
        echo "${line#$prefix}" >> .tmp_chr
    done < chromosome_$file
    mv .tmp_chr chromosome_$file
else
    ./extract_column.sh $file $var_header chromosome
fi
