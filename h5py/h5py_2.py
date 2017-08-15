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
ramdom_blocks_for_chr = genfromtxt(csvf, delimiter = '\t', usecols=(3))

print "Loaded csv file: ", csvf

f = h5py.File(h5file, 'a')

if trait in f:
    trait_group = f[trait]
else:
    trait_group = f.create_group(trait)

for i in range(1,22):
    try:
        cg = trait_group.create_group(str(i))
        for j in range(0, 8):
            cg.create_group((str(j)))
    except ValueError:
        print "Chromosomes already exist"

for i in range(1,22):
    # get the array slice where chromosome position == i
    # from that slice keep the first column, i.e. the snpvalues (we know the chromosome)
    chr_mask = [pvalarray[:,1] == i]
    vals_chr = pvalarray[chr_mask][:,0]
    snps_chr = snparray[chr_mask]
    blocks = ramdom_blocks_for_chr[chr_mask]
    chrom_group = trait_group[str(i)]

    for b in range(0, 8):
        # get the array slice for chr i where block == b
        block_mask = blocks == b
        vals = vals_chr[block_mask]
        snps = snps_chr[block_mask]
        if (vals.size != 0):
            block_group = chrom_group[str(b)]
            
            for j in range(0,len(snps)):
                try:
                    snp_group = block_group.create_group(snps[j])
                    d = np.array([1, vals[j]])
                    snp_group.create_dataset('pvals', data=d, maxshape = (None,))
                    d = np.array(['s', study])
                    snp_group.create_dataset('studies', data=d, maxshape = (None,)) 
                except ValueError:
                    snp_group = block_group[snps[j]]
                    pvals_dset = snp_group['pvals']
                    studies_dset = snp_group['studies']
                    
                    pvals_dset.resize((pvals_dset.shape[0] + 1,))
                    pvals_dset[-1] = vals[j]
                    studies_dset.resize((studies_dset.shape[0] + 1,))
                    studies_dset[-1] = study


