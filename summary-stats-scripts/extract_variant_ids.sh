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

echo -n "Are there any variant ids we need to exclude? Yes or No and press [ENTER]: "
read exclude

yes='Yy'
if [[ $exclude =~ [$yes] ]];then
    echo ""
    echo "Please enter a comma separated list of what we will need to exclude"
    echo "Example: if we need to exclude all entries that look like: MERGED_DEL_2_58234 and imm_1_247639"
    echo "then please type: MERGED_DEL,imm"
    echo ""
    echo -n "Enter the comma separeted list and press [ENTER]: "
    read types_to_exclude
fi

if [ -z $types_to_exclude ]; then
    echo "No types to exclude"
    echo "Proceding with variant id exctraction"
    ./extract_column.sh $file $var_header variant
else
    echo "Types to exclude: $types_to_exclude"
    ignore=$(echo "^$types_to_exclude" | sed 's/,/\\|^/g')
    ./extract_column.sh $file $var_header variant
    cat variant_$file | grep -v "$ignore" > variant_ids_$file
    rm variant_$file
fi

