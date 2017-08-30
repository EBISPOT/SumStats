"""
    Stores the data in the hierarchy of Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    snparray will hold the snp ids
    pvals will hold each snps pvalue for this study
    chr will hold each snps position
    or_array will hold each snps odds ratio for this study
    we can add any other information that we want

    the positions in the vectors correspond to each other
    snparray[0], pvals[0], chr[0], and or_array[0] hold the information for SNP 0

"""


import h5py
from numpy import genfromtxt
import argparse

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


study_group.create_dataset('snps', data=snparray)
study_group.create_dataset('pvals', data=pvals)
study_group.create_dataset('chr', data=chr)
study_group.create_dataset('or', data=or_array)
