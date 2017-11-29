#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""

file=$1
var_header=$2
element=$3
base=$(dirname "$0")

if [ -z $file ] || [ -z $var_header ] || [ -z $element ];
then
    echo ""
    echo "$0 not enough parameters provided! Exiting..."
    echo ""
    exit
fi

echo -n "Does the column have more data than just the $element? type [y] or [n] and press [ENTER]: "
read has_more_data

yes='Yy'
if [[ $has_more_data =~ [$yes] ]];then
    echo ""
    echo -n "Type the delimiter that separates the data in this column? (e.g. , : - ) and press [ENTER]: "
    read column_delimiter
    if [ -z $column_delimiter ]; then
        echo ""
        echo "No delimiter entered! Exiting..."
        echo ""
        exit 1
    fi
    echo ""
    echo "What is the position of \"$element\" based on the \"$column_delimiter\" delimiter?"
    echo -e "${GREEN}Example:${NC} for extracting BP from \"chr1:3456\" with delimiter \":\", you need to type in \"2\""
    echo ""
    echo -n "Type in the position and press [ENTER]: "
    read position
    if [ -z $position ]; then
         echo "No position entered! Exiting..."
         exit 1
    fi
    echo ""

fi
echo "Starting column extraction..."
$base/strip_column.sh $file $var_header $column_delimiter $position > "$element"_"$file"
echo "Column extraction done!"

