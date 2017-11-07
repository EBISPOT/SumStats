#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

file=$1

if [ -z $file ];then
    echo "You haven't specified a file!"
    exit 1
fi
echo ""
echo -e "Below You can see the header of the file and the first line of data"
echo -e "${GREEN}-----------------${NC}"
echo ""
awk '{
if (NR == 1){
 for (i = 1; i <=NF; i++){
	 h[$i]=i
 }}else{
 if (NR == 2){
	 for (key in h){
		 print key " : " $h[key]
	 }
 }else {exit}}}' $file

echo ""
echo -e "${GREEN}-----------------${NC}"
