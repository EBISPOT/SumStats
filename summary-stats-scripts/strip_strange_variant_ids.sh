#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

file=$1
base=$(dirname "$0")

if [ -z $file ]; then
    echo "File name not specified! Exiting..."
    exit 1
fi

$base/peek.sh $file
echo -ne "Enter the variant id header and press [ENTER]: "
read var_header

if [ -z $var_header ]; then
    echo "Variant header not specified! Exiting..."
    exit 1
fi
echo "Searching for strange variant ids..."

cp $file "$file"_clean

$base/strip_column.sh $file $var_header | sort | uniq | grep -v "^rs" | grep -v "^ch" > strange_variant_ids_"$file"
rm "$file"_clean

if [ -s strange_variant_ids_"$file" ]; then
    echo -e "The strange variant IDs are saved in the ${GREEN} strange_variant_ids_$file ${NC} file"
else
    echo "The file has no strange variant ids"
fi
