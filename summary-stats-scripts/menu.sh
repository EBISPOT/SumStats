#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""

file=$1
base=$(dirname "$0")

if [ -z $file ];
then
    echo -e "${RED}You need to run the script with the file name as a parameter"
    echo -e "${RED}Example: menu.sh sum-stats-file.csv"
    echo -e "${NC}"
    exit
fi
if [ ! -s "$file" ]; then
    echo -e "${RED}File $file does not exist!${NC}"
    exit
fi
clear
echo "Pre-processing file, please wait..."
dos2unix $file
$base/make_tab.sh $file
mv .tab $file

echo ""
pwd
echo ""
echo -e "${GREEN}Running script for $file file!${NC}"
echo ""
PS3='Please enter your choice (ENTER to show the list of options): '
options=("Select first 50 lines"
       "Select first 50 lines of file"
       "Peek into file"
       "List all files in directory"
       "Create directory for file"
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
       "Delete all intermediate files"
       "Delete specific file"
       "Quit")

select opt in "${options[@]}"
do
case $opt in
    "Select first 50 lines")
        $base/select_first_50.sh $file
        ;;
    "Select first 50 lines of file")
        $base/select_lines_from_file.sh
        ;;
    "Peek into file")
        $base/peek.sh $file
        ;;
    "List all files in directory")
        ls | grep -v .sh
        ;;
    "Create directory for file")
        echo "Creating new directory and copying file there..."
        mkdir sum-stats-dir-$file
        cp $file sum-stats-dir-$file
        cd sum-stats-dir-$file
        echo -e "Created directory called: ${GREEN}sum-stats-dir-$file ${NC} and copied $file there"
        ;;
    "Extract variant")
        $base/extract_simple.sh $file "variant" "variant"
        ;;
    "Extract chromosome")
            $base/extract_simple.sh $file "chromosome" "chr"
        ;;
    "Extract base pair location")
        	$base/extract_simple.sh $file "base pair location" "bp"
        ;;
    "Extract effect")
        	$base/extract_simple.sh $file "minor allele" "effect"
        ;;
    "Extract other")
        	$base/extract_simple.sh $file "reference allele" "other"
        ;;
    "Extract frequency")
        	$base/extract_simple.sh $file "minor allele frequency in controls" "freq"
        ;;
    "Extract odds ratio")
        	$base/extract_simple.sh $file "odds ratio" "or"
        ;;
    "Extract standard error")
        	$base/extract_simple.sh $file "standard error" "se"
        ;;
    "Extract beta")
        	$base/extract_simple.sh $file "beta" "beta"
        ;;
    "Extract p-value")
        	$base/extract_simple.sh $file "p-value" "pval"
        ;;
    "Extract range")
        	$base/extract_simple.sh $file "range" "range"
        ;;
    "Combine all info")
        	$base/combine_all_info.sh $file
        ;;
    "Delete all intermediate files")
        $base/delete_all_intermediates.sh $file
        ;;
    "Delete specific file")
        $base/delete_file.sh
        ;;
    "Quit")
        break
        ;;
    *)
        echo "invalid option"
        ;;
 esac
done
