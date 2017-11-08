#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""

file=$1
var_header=$2
element=$3

if [ -z $file ] || [ -z $var_header ] || [ -z $element ];
then
    echo "$0 not enough parameters provided! Exiting..."
    exit
fi

echo -n "Does the column have more data than just the $element? type y or n and press [ENTER]: "
read has_more_data

yes='Yy'
if [[ $has_more_data =~ [$yes] ]];then
    echo ""
    echo -n "What delimiter separates the data in this column? (e.g. , : - ) type the delimiter and press [ENTER]: "
    read column_delimiter
    if [ -z $column_delimiter ]; then
        echo "No delimiter entered! Exiting..."
        exit 1
    fi
    echo "If I separate the column based on this delimiter, what position does the $element have? Example: 34590:chr1_A_D then you need to type 2"
    echo -n "Type the number and press [ENTER]: "
    read position
    if [ -z $position ]; then
         echo "No position entered! Exiting..."
         exit 1
    fi
    echo ""
    echo -n "Is there anything else attached to the end of the information that we need to clean? (Example: 34590:chr1_A_D) then type \"y\" else type \"n\" and press [ENTER]: "
    read more_cleaning
    if [[ $more_cleaning =~ [$yes] ]];then
        echo -n "What does the first characted after our info look like? (For the above example I would type \"_\"). Type the character and press [ENTER]: "
        read extra_cleanup
        if [ -z $extra_cleanup ]; then
          echo "No character entered! Exiting..."
          exit 1
        fi
    fi
fi

./strip_column.sh $file $var_header $column_delimiter $position $extra_cleanup > "$element"_"$file"

