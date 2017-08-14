import h5py
import numpy as np
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('HDF5_output_file', help = 'The name of the HDF5 file')
parser.add_argument('study_name', help = 'The study I am looking for')
parser.add_argument('trait_name', help = 'The trait I am looking for')
parser.add_argument('snp', help = 'The SNP I am looking for')

args = parser.parse_args()

h5file = args.HDF5_output_file 
study = args.study_name 
trait = args.trait_name
snp = args.snp

f = h5py.File(h5file, mode = "r")

g = f[trait + "/" + study]

snps_dset = g['snps']
pvals_dset = g['pvals']
chr_dset = g['chr']

snps = snps_dset[:]
masks = snps == snp

print pvals_dset[masks]
print chr_dset[masks]

#pvals = pvals_dset[:]

#maskv = pvals > 0.11

#print len(snps_dset[maskv])
