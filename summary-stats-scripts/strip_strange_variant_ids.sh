#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

file=$1
var_header=$2

if [ -z $file ] || [ -z $var_header ]; then
    echo "File name and variant header not specified!"
    exit 1
fi

if awk '{exit !/\t/}' $file ; then
    delimiter="\t"
elif awk '{exit !/ /}' $file ; then
    delimiter=" "
elif awk '{exit !/,/}' $file ; then
    delimiter=","
else
    echo "The file is neither comma, tab or space delimited!"
    echo "Can not do anything"
    exit 1
fi

awk 'BEGIN{FS="'$delimiter'"}
{
    if (NR == 1){
        for (i = 1; i <=NF; i++){
            h[$i]=i
        }
    }
    else {
        for ( key in h) {
            if (key == "'$var_header'"){
                print $h[key]
            }
        }
    }
}' $file | sort | uniq | grep -v "^rs" | grep -v "^ch" > strange_variant_ids_"$file"

if [ -s strange_variant_ids_"$file" ]; then
    echo -e "The strange variant IDs are saved in the ${GREEN} strange_variant_ids_$file ${NC} file"
else
    echo "The file has no strange variant ids"
fi
