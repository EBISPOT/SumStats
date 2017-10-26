#!/bin/bash

file=$1
base=$(pwd);
templates=$base/templates
study=$(echo "$file" | cut -d"-" -f2)
trait=$(echo "$file" | cut -d"-" -f3)

for i in {1..23}
do
    # check to see if it exists
    if [ -s $base/files/toload/chr"$i"_"$file" ];
    then
        cd $base
        mkdir chr_config$i
        cp $templates/chr_config.yml $base/chr_config$i/config.yml
        cd $base/chr_config$i

        sed 's/load_file/chr'$i'_'$file'/' config.yml > tmp
        mv tmp config.yml
        sed 's/save_file/file_'$i'.h5/' config.yml > tmp
        mv tmp config.yml
        sed 's/study_config/'$study'/' config.yml > tmp
        mv tmp config.yml
        sed 's/trait_config/'$trait'/' config.yml > tmp
        mv tmp config.yml
        cd $base
    fi
done
