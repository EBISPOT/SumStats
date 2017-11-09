#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

file=$1

awk '{if(NR < 51){print}else{exit}}' $file > first_50_"$file"
echo -e "Created file with first 50 lines called ${GREEN}first_50_"$file"${NC}"
