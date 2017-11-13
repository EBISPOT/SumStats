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
       "Get all unconventional variant ids"
       "Look at found strange variant ids"
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
       "Explain options"
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
    "Get all unconventional variant ids")
        $base/strip_strange_variant_ids.sh $file
        ;;
    "Look at found strange variant ids")
        if [ ! -s strange_variant_ids_"$file" ];then
            echo "File does not exist. Might be that there are no strange"
            echo "variant ids or that you didn't request for them to be found."
        else
            echo ""
            echo -e "${GREEN}Opening list of strange variants, press [ENTER] to view more or [q] to close the file${NC}"
            echo ""
            more strange_variant_ids_"$file"
        fi
        ;;
    "Extract variant")
        $base/extract_variant_ids.sh $file
        ;;
    "Extract chromosome")
        if [ ! -s "$file"_clean ];then
            echo "You first need to extract the variant column before you proceed"
        else
            $base/extract_simple.sh $file "chromosome" "chr"
        fi
        ;;
    "Extract base pair location")
		if [ ! -s "$file"_clean ];then
             echo "You first need to extract the variant column before you proceed"
        else
        	$base/extract_simple.sh $file "base pair location" "bp"
		fi
        ;;
    "Extract effect")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
         else
        	$base/extract_simple.sh $file "minor allele" "effect"
		fi
        ;;
    "Extract other")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
         else
        	$base/extract_simple.sh $file "reference allele" "other"
		fi
        ;;
    "Extract frequency")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
         else
        	$base/extract_simple.sh $file "minor allele frequency in controls" "freq"
		fi
        ;;
    "Extract odds ratio")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
         else
        	$base/extract_simple.sh $file "odds ratio" "or"
		fi
        ;;
    "Extract standard error")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
         else
        	$base/extract_simple.sh $file "standard error" "se"
		fi
        ;;
    "Extract beta")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
         else
        	$base/extract_simple.sh $file "beta" "beta"
		fi
        ;;
    "Extract p-value")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
         else
        	$base/extract_simple.sh $file "p-value" "pval"
		fi
        ;;
    "Extract range")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
         else
        	$base/extract_simple.sh $file "range" "range"
		fi
        ;;
    "Combine all info")
		if [ ! -s "$file"_clean ];then
              echo "You first need to extract the variant column before you proceed"
        else
        	$base/combine_all_info.sh $file
		fi
        ;;
    "Delete all intermediate files")
        $base/delete_all_intermediates.sh $file
        ;;
    "Delete specific file")
        $base/delete_file.sh
        ;;
    "Explain options")
        $base/explain.sh $file
        ;;
    "Quit")
        break
        ;;
    *)
        echo "invalid option"
        ;;
 esac
done
