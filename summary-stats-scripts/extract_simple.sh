#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
clear
echo ""

file=$1
long_name=$2
short_name=$3
base=$(dirname "$0")

if [ -z "$file" ] || [ -z "$long_name" ] || [ -z "$short_name" ] ;
then
    echo ""
    echo "$0 You need to provide the correct arguments! Exiting..."
    echo ""
    exit
fi

$base/peek.sh $file

echo -ne "Enter the $long_name ($short_name) header (NA if missing) and press [ENTER]: "
read var_header

if [ -z $var_header ] ; then
    echo ""
    echo "You need to specify header for $short_name!. Exiting..."
    echo ""
    exit
fi

if [ $var_header == "NA" ];then
    awk '{print "-1"}' "$file" > "$short_name"_"$file"
else
    # check if the header is in the file or not
    if ! awk '{print;exit}' $file | grep -q $var_header ; then
        echo ""
        echo "Wrong header entered. Exiting..."
        echo ""
        exit
    fi
    $base/extract_column.sh "$file" $var_header $short_name
    echo -en "${GREEN}Showing first line of data from the extracted column:${NC} "
    awk '{print;exit}' "$short_name"_"$file"
    echo ""
	echo -ne "Enter any prefix - to be removed - (if any) and press [ENTER], OR just press [ENTER]: "
	read prefix

    echo -ne "Enter any suffix - to be removed - (if any) and press [ENTER], OR just press [ENTER]: "
    read suffix
	if [ ! -z $prefix ] || [ ! -z $suffix ] ;then
        echo ""
        echo "Removing prefix and/or suffix, please wait..."
         while read line; do
             no_prefix=${line#$prefix}
             no_suffix=${no_prefix%$suffix}
             echo "${no_suffix}" >> .tmp
         done < "$short_name"_"$file"
         mv .tmp "$short_name"_"$file"
         echo "Done!"
	fi
fi
echo -e "File saved in: ${GREEN} "$short_name"_"$file"${NC} "
echo ""
