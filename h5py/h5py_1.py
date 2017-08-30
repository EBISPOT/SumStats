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

pvals = genfromtxt(csvf, delimiter = '\t', usecols=(1))
chr = genfromtxt(csvf, delimiter = '\t', usecols=(2))
snparray = genfromtxt(csvf, delimiter = '\t', usecols=(0), dtype=None)
orarray = genfromtxt(csvf, delimiter = '\t', usecols=(3))

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

#TODO: sort by chromosome store the whole dataset
#srted = sorted(myarray, key = itemgetter(2))

# sort the chrom positions
#chr.sort()

# sort pvals and snps accordingly

#snparray = snparray[chr]
#pvals = pvals[chr]

study_group.create_dataset('snps', data=snparray)
study_group.create_dataset('pvals', data=pvals)
study_group.create_dataset('chr', data=chr)
study_group.create_dataset('or', data=orarray)
