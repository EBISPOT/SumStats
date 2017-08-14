import h5py
import numpy as np
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('HDF5_output_file', help = 'The name of the HDF5 file')
parser.add_argument('study_name', help = 'The study I am looking for')
parser.add_argument('trait_name', help = 'The trait I am looking for')
parser.add_argument('chrp', help = 'The chromosome of the snp I am looking for')
parser.add_argument('snp', help = 'The SNP I am looking for')
args = parser.parse_args()

h5file = args.HDF5_output_file 
study = args.study_name 
trait = args.trait_name
chr = args.chrp
snp = args.snp

f = h5py.File(h5file, mode = "r")

table = f[trait + "/" + study + "/" + str(chr) + "/" + snp]

print table[...]
