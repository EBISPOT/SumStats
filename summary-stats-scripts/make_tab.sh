#!/bin/bash

file=$1

if awk '{exit !/\t/}' "$file"; then cp $file .tab; fi
if [ ! -f .tab ]; then
	echo "The file is not a TAB file. Converting..."
	if awk '{exit !/,/}' "$file"; then tr ',' \\t < $file > .tab;
    elif awk '{exit !/ /}' "$file"; then tr ' ' \\t < $file > .tab; fi
fi

