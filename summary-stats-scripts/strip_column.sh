#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

file=$1
col_header=$2
extra_delimiter=$3
position=$4
extra_filtering_character=$5

if [ -z $file ] || [ -z $col_header ]; then
    echo "File name and column header not specified!"
    exit 1
fi


function get_column () {

awk 'BEGIN{FS="\t"}
     {
         if (NR == 1){
             for (i = 1; i <=NF; i++){
                 h[$i]=i
             }
         }
         else {
             for ( key in h) {
                 if (key == "'$col_header'"){
                     print $h[key]
                 }
             }
         }
     }' $file

}

if [ -z "$extra_delimiter" ] && [ -z "$position" ]; then
	get_column
    exit
else
	get_column > .column_$file
	awk 'BEGIN{FS="'$extra_delimiter'"}{
		print $'$position'
	}' .column_$file > .info_from_position_$file
	rm .column_$file

	if [ ! -z "$extra_filtering_character" ];then
		while read line; do
			echo "$line" | cut -d"$extra_filtering_character" -f1
		done < .info_from_position_$file
	else
		awk '{print}' .info_from_position_$file
	fi
	rm .info_from_position_$file
fi
