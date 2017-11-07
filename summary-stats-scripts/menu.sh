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
       "Extract variant ids"
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
    "Extract variant ids")
        ./extract_variant_ids.sh $file
        ;;
    "Quit")
        break
        ;;
    *)
        echo "invalid option"
        ;;
 esac
done
