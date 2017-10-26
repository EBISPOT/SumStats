#!/bin/bash

file=$1
base=$(pwd);
templates=$base/templates
study=$(echo "$file" | cut -d"-" -f2)
trait=$(echo "$file" | cut -d"-" -f3)

    cd $base
    mkdir trait_config
    cp $templates/trait_config.yml $base/trait_config/config.yml
    cd $base/trait_config

    sed 's/load_file/'$file'/' config.yml > tmp
    mv tmp config.yml
    sed 's/save_file/file_'$trait'.h5/' config.yml > tmp
    mv tmp config.yml
    sed 's/study_config/'$study'/' config.yml > tmp
    mv tmp config.yml
    sed 's/trait_config/'$trait'/' config.yml > tmp
    mv tmp config.yml
    cd $base

