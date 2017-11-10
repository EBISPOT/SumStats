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
    echo "$0 You need to provide the correct arguments! Exiting..."
    exit
fi

$base/peek.sh $file

echo -ne "Enter the $long_name ($short_name) header (NA if missing) and press [ENTER]: "
read var_header

if [ -z $var_header ] ; then
    echo "You need to specify header for $short_name, or NA if missing). Exiting..."
    exit
fi

if [ $var_header == "NA" ];then
    awk '{print "-1"}' "$file" > "$short_name"_"$file"
else
    $base/extract_column.sh "$file" $var_header $short_name
    echo -n "Showing first line of extracted column: "
    awk '{print;exit}' "$short_name"_"$file"

	echo -ne "Enter any prefix - to be removed - (if any) and press [ENTER], OR just press [ENTER]: "
	read prefix

    echo -ne "Enter any suffix - to be removed - (if any) and press [ENTER], OR just press [ENTER]: "
    read suffix

	if [ ! -z $prefix ] || [ ! -z $suffix ] ;then
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
