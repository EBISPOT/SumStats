import h5py
import numpy as np
from numpy import genfromtxt
import argparse
import hashlib
from operator import itemgetter

parser = argparse.ArgumentParser()
parser.add_argument('CSV_input_file', help = 'The file to be loaded')
parser.add_argument('HDF5_output_file', help = 'The name of the HDF5 file to be created/updated')
parser.add_argument('study_name', help = 'The name of the first group this will belong to')
parser.add_argument('trait_name', help = 'The name of the trait the SNPs of this file are related to')
args = parser.parse_args()

csvf = args.CSV_input_file
h5file = args.HDF5_output_file
study = args.study_name
trait = args.trait_name

pvalarray = genfromtxt(csvf, delimiter = '\t', usecols=(1,2))
snparray = genfromtxt(csvf, delimiter = '\t', usecols=(0), dtype=object)

print "Loaded csv file: ", csvf

f = h5py.File(h5file, 'a')

if trait in f:
    trait_group = f[trait]
    if study in trait_group:
        study_group = trait_group[study]
    else:
        study_group = trait_group.create_group(study)
else:
    study_group = f.create_group(trait + "/" + study)

for i in range(1,22):
    try:
        trait_group.create_group(str(i))
    except ValueError:
        print "Chromosomes already exist"

for i in range(1,22):
    # get the array slice where chromosome position == i
    # from that slice keep the first column, i.e. the snpvalues (we know the chromosome)
    chr_mask = [pvalarray[:,1] == i]
    vals = pvalarray[chr_mask][:,0]
    snps = snparray[chr_mask]
    if (vals.size != 0):
        chrom_group = trait_group[str(i)]
        for j in range(0,len(snps)):
            try:
                chrom_group.create_dataset(snps[j], data = vals[j])
            except ValueError:
                print snps[j] + " already exists!"

 
