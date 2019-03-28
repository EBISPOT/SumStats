#!/bin/bash 

base=$(cd ${0%/*}/..; pwd)

file=$1
config="$SS_CONFIG"
to_load_location=$SS_LOAD

if [ -z $file ]; then
        echo "Need to provide the file (full path). Exiting..."
        exit
fi

if [ -z $config ]; then
        echo "Need to set the SS_CONFIG env variable (without trailing slash, full path). Exiting..."
        exit
fi

if [ -z $to_load_location ]; then
        echo "Need to set the SS_LOAD env variable (without trailing slash, full path) to the path where the files to be loaded live. Exiting..."
        exit
fi

count=$(bjobs -g /sumstatsloader | wc -l)
while [ "$count" -gt "0" ]; do
        echo "Some jobs are running, wait till they finish to submit another study!"
        echo "Exiting..."
        exit
done

filename=$(basename $file)
name=$(echo $filename | cut -f 1 -d '.')
echo "FILE: $file"

#bp_step=$(grep bp_step $config | cut -d":" -f2 | sed 's/\"//g; s/,//g; s/ //g')
#available_chromosomes=$(grep available_chromosomes $config | cut -d":" -f2 | sed 's/\"//g; s/,//g; s/ //g')

# pre-process the file
filename="$filename"

name=$(echo $filename | cut -f 1 -d '.')
study=$(echo "$name" | cut -d"-" -f2)
trait=$(echo "$name" | cut -d"-" -f3) 

echo $study
echo $trait  


#bsub -q production-rh7 -eo stderr -M 2400 -R "rusage[mem=2400]" "singularity exec docker://rcsa/python3-hdf5 python ${ss_dir}/load_ss.py -f $dataset  -trait $trait -hdf $ss_dir/${study}.h5 -study $study"



#bsub -K -o $base/output.txt -e $base/error.txt python $base/bin/preparation/setup_configuration.py -f $file -config $config -create
#
#for i in `seq 1 $available_chromosomes`;
#do
#	$base/bin/load/submit_chr.sh $name $i $to_load_location
#	for bp in `seq 1 $bp_step`; do
#		$base/bin/load/submit_snp.sh $name $i $bp $to_load_location
#	done
#done
#$base/bin/load/submit_trait.sh $filename $to_load_location
