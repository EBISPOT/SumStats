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
echo -ne "Enter the variant id header and press [ENTER]: "
read var_header

./strip_strange_variant_ids.sh $file $var_header
