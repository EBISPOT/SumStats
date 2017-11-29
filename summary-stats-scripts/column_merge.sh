#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
clear
echo ""

file=$1
base=$(dirname "$0")

if [ -z "$file" ] ;
then
    echo "$0 You need to provide the correct arguments! Exiting..."
    exit
fi

$base/peek.sh $file

echo -ne "Enter the header of the first column to be mergerd and press [ENTER]: "
read header_1

if [ -z $header_1 ] ; then
    echo "You didn't specify a header for merging. Exiting..."
    exit
fi

echo -ne "Enter the header of the second  column to be mergerd and press [ENTER]: "
read header_2

if [ -z $header_2 ]; then
    echo "You didn't specify a header for merging. Exiting..."
    exit
fi

echo  -ne "Enter the delimiter of the merged columns (if none will be delimited by a dash \"-\") [ENTER]:"
read delimiter

if [ -z $delimiter ];then
    echo "You didn't specify a delimiter to separate the columns, using dash!"
    delimiter="-"
fi
echo ""
echo "Merging columns, please wait..."
# exclude the colums from the file and
column_one_position=$(awk 'BEGIN{FS="\t"}
      {
          if (NR == 1){
              for (i = 1; i <=NF; i++){
                  if($i == "'$header_1'"){
					print i; exit;
				  }
              }
          }else{exit}
      }' $file)

if [ -z $column_one_position ]; then
	echo -e "${GREEN}$header_1${NC} not found in file! Exiting..."
	exit
fi

 column_two_position=$(awk 'BEGIN{FS="\t"}
       {
           if (NR == 1){
               for (i = 1; i <=NF; i++){
                   if($i == "'$header_2'"){
                     print i; exit;
                   }
               }
           }else{exit}
       }' $file)

 if [ -z $column_two_position ]; then
     echo -e "${GREEN}$header_2${NC} not found in file! Exiting..."
     exit
 fi


awk 'BEGIN{FS="\t";OFS="\t"; ind=1}{
	if (NR == 1){
    	for (i = 1; i <=NF; i++){
			if (i != '$column_one_position' && i != '$column_two_position'){
				h[ind]=i;
                ind++;
			}
		}
	}
    for (mykey=1; mykey<ind;mykey++){
        if(mykey == (ind - 1) ){
            printf "%s",$h[mykey]
        } else {
             printf "%s\t",$h[mykey]
        }
    }
    printf "\n"
}' $file > .without_headers

 awk 'BEGIN{FS="\t";OFS="'$delimiter'"}{
	print $'$column_one_position',$'$column_two_position'
 }' $file > .only_headers

 paste -d"\t" .without_headers .only_headers > $file
 rm .without_headers .only_headers
 echo "Done!"
 echo ""
 echo "You can use \"Peek into file\" to see the result or \"Refresh original file\" to revert the changes!"
 echo ""
