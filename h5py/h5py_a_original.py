"""
    Stored as CHR/SNP/DATA
    Where DATA is:
    pvals: a vector that holds the p-values for this SNP/Trait association
    or: a vector that holds the OR value for this SNP/Trait association
    studies: a vector that holds the studies that correspond to the p-values for this SNP/Trait association

    can add more information if needed
"""

import h5py
import numpy as np
from numpy import genfromtxt
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('CSV_input_file', help = 'The file to be loaded')
parser.add_argument('HDF5_output_file', help = 'The name of the HDF5 file to be created/updated')
parser.add_argument('study_name', help = 'The name of the first group this will belong to')
# parser.add_argument('trait_name', help = 'The name of the trait the SNPs of this file are related to')
args = parser.parse_args()

csvf = args.CSV_input_file
h5file = args.HDF5_output_file
study = args.study_name
# trait = args.trait_name
print(time.strftime('%a %H:%M:%S'))

# snp id is a string, so dtype = None
snparray = genfromtxt(csvf, delimiter = '\t', usecols = (0), dtype = None)
pvalarray = genfromtxt(csvf, delimiter = '\t', usecols = (1), dtype = float)
chrarray = genfromtxt(csvf, delimiter = '\t', usecols = (2), dtype = int)
orarray = genfromtxt(csvf, delimiter = '\t', usecols = (3), dtype = float)

print "Loaded csv file: ", csvf
print(time.strftime('%a %H:%M:%S'))


# Open the file with read/write permissions and create if it doesn't exist
f = h5py.File(h5file, 'a')

# if trait in f:
#     trait_group = f[trait]
# else:
#     trait_group = f.create_group(trait)

# for the trait, create a group for every chromosome

for i in range(1,22):
    if str(i) not in f:
        f.create_group(str(i))

if "X" not in f:
    f.create_group("X")
if "Y" not in f:
    f.create_group("Y")
if "MT" not in f:
    f.create_group("MT")

for i in range(1,2):
    print(time.strftime('%a %H:%M:%S'))
    print "Chromosome:", i
    # get the array slice where chromosome position == i
    # from that slice keep the first column, i.e. the snpvalues (we know the chromosome)
    chr_mask = [chrarray == i]
    pvals = pvalarray[chr_mask]
    snps = snparray[chr_mask]

    chrom_group = f[str(i)]

    if pvals.size != 0:
        for j in xrange(len(snps)):

            if j % 1000000 == 0:
                print "Loaded %s so far..." % (j)
                print(time.strftime('%a %H:%M:%S'))

            snp_group = chrom_group.get(snps[j])
            if snp_group is None:
                snp_group = chrom_group.create_group(snps[j])

                # creating the datasets with maxshape = ((None,)) so they can be extended
                # max actual number of values we can store per array is 2^64 - 1

                d = np.array([pvals[j]])
                snp_group.create_dataset('pvals', data=d, maxshape = (None,), compression="gzip")
                d = np.array([study])
                snp_group.create_dataset('studies', data=d, maxshape = (None,), compression="gzip")
                d = np.array([orarray[j]])
                snp_group.create_dataset('or', data=d, maxshape = (None,), compression="gzip")
            else:
                # reading the existing datasets and expanding them by 1
                # the expansion can happen once for every new file/study that we load
                pvals_dset = snp_group['pvals']
                studies_dset = snp_group['studies']
                or_dset = snp_group['or']

                pvals_dset.resize((pvals_dset.shape[0] + 1,))
                pvals_dset[-1] = pvals[j]
                studies_dset.resize((studies_dset.shape[0] + 1,))
                studies_dset[-1] = study
                or_dset.resize((or_dset.shape[0] + 1,))
                or_dset[-1] = orarray[j]



