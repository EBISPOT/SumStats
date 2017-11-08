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

echo ""
pwd
echo ""
echo -e "${GREEN}Running script for $file file!${NC}"
echo ""
PS3='Please enter your choice (ENTER to show the list of options): '
options=("Select first 50 lines"
       "Peek into file"
       "Get all unconventional variant ids"
       "Extract variant"
       "Extract chromosome"
       "Extract base pair location"
       "Extract effect"
       "Extract other"
       "Extract frequency"
       "Extract odds ratio"
       "Extract standard error"
       "Extract beta"
       "Extract p-value"
       "Extract range"
       "Combine all info"
       "Quit")

select opt in "${options[@]}"
do
case $opt in
    "Select first 50 lines")
        awk '{if(NR < 51){print}else{exit}}' $file > first_50_"$file"
        echo -e "Created file with first 50 lines called ${GREEN}first_50_"$file"${NC}"
        ;;
    "Peek into file")
        ./peek.sh $file
        ;;
    "Get all unconventional variant ids")
        ./get_all_strange_variant_ids.sh $file
        ;;
    "Extract variant")
        ./extract_variant_ids.sh $file
        ;;
    "Extract chromosome")
        ./extract_chromosome.sh $file
        ;;
    "Extract base pair location")
        ./extract_simple.sh $file "base pair location" "bp"
        ;;
    "Extract effect")
        ./extract_simple.sh $file "minor allele" "effect"
        ;;
    "Extract other")
        ./extract_simple.sh $file "reference allele" "other"
        ;;
    "Extract frequency")
        ./extract_simple.sh $file "minor allele frequency in controls" "freq"
        ;;
    "Extract odds ratio")
        ./extract_simple.sh $file "odds ratio" "or"
        ;;
    "Extract standard error")
        ./extract_simple.sh $file "standard error" "se"
        ;;
    "Extract beta")
        ./extract_simple.sh $file "beta" "beta"
        ;;
    "Extract p-value")
        ./extract_simple.sh $file "p-value" "pval"
        ;;
    "Extract range")
        ./extract_simple.sh $file "range" "range"
        ;;
    "Combine all info")
        ./combine_all_info.sh $file
        ;;
    "Quit")
        break
        ;;
    *)
        echo "invalid option"
        ;;
 esac
done
