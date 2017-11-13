#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
base=$(dirname "$0")
echo ""

echo -n "Enter the name of the file that you want to delete and press [ENTER]: "
read file

if [ -z $file ] ;
then
    echo "You didn't enter a file! Exiting..."
    exit
fi

if [ -s "$file" ];then
    $base/select_first_50.sh $file
else
    echo "$file does not exist!"
fi

