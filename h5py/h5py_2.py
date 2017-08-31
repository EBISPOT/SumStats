"""
    Stores the data in the hierarchy of Trait/Study/SNP/DATA
    where DATA:

    vector that has in position 0 the p-value, in position 1 the chromosome, in position 2 the OR value
    for this study/snp association
    we can add more data if we want to to this vector
"""


import h5py
from numpy import genfromtxt
import argparse
import numpy as np

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

# snp id is a string, so dtype = None
snparray = genfromtxt(csvf, delimiter = '\t', usecols = (0), dtype = None)
pvals = genfromtxt(csvf, delimiter = '\t', usecols = (1), dtype = float)
chr = genfromtxt(csvf, delimiter = '\t', usecols = (2), dtype = int)
or_array = genfromtxt(csvf, delimiter = '\t', usecols = (3), dtype = float)

print "Loaded csv file: ", csvf

# Open the file with read/write permissions and create if it doesn't exist
f = h5py.File(h5file, 'a')

if trait in f:
    trait_group = f[trait]
    if study in trait_group:
        study_group = trait_group[study]
    else:
        study_group = trait_group.create_group(study)
else:
    study_group = f.create_group(trait + "/" + study)

# loop through the snp array and for each SNP
# 1. create the dataset that will have [pvalue, chromosome, OR] for that SNP/Study/Trait association
# 2. save that dataset under the SNPs name
for i in xrange(len(snparray)):
    dataset = np.array([pvals[i], chr[i], or_array[i]])
    study_group.create_dataset(snparray[i], data=dataset)