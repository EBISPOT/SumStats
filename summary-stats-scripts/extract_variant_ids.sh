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
clear

$base/peek.sh $file

echo ""
echo "We will by default exclude anything that doesn't have an rsid or doesn't start with chr (e.g. chr1:34230)"
echo -n "Are there any extra variant ids we need to include? [y] or [n] and press [ENTER]: "
read include

yes='Yy'
if [[ $include =~ [$yes] ]];then
    echo ""
    echo "Please enter a comma separated list of any other pattern that you would like to include"
    echo "Example: if we need to include all entries that look like: MERGED_DEL_2_58234 and imm_1_247639"
    echo "then please type: MERGED_DEL,imm"
    echo ""
    echo -n "Enter the comma separeted list and press [ENTER]: "
    read types_to_include
fi

if [ ! -z $types_to_include ];then
    echo "Types to include: $types_to_include"
    find_pattern=$(echo "^$types_to_include" | sed 's/,/\\|^/g')
fi
if [ ! -z $find_pattern ];then
    find_pattern="$find_pattern\\|^rs\\|^ch"
else
    find_pattern="^rs\\|^ch"
fi
echo "Cleaning up any stray variant ids..."
cat $file | grep "$find_pattern" | grep -v "^\.\|NA" > "$file"_clean

awk '{print;exit}' $file | cat - "$file"_clean > .tmp
mv .tmp "$file"_clean

$base/extract_simple.sh "$file" "variant id" variant












