#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

file=$1
var_header=$2
base=$(dirname "$0")

if [ -z $file ] || [ -z $var_header ]; then
    echo "File name and variant header not specified!"
    exit 1
fi

$base/strip_column.sh $file $var_header | sort | uniq | grep -v "^rs" | grep -v "^ch" > strange_variant_ids_"$file"

if [ -s strange_variant_ids_"$file" ]; then
    echo -e "The strange variant IDs are saved in the ${GREEN} strange_variant_ids_$file ${NC} file"
else
    echo "The file has no strange variant ids"
fi
