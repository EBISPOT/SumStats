"""
    Database design looks like:
    a 2D array where each element is a triple: (SNPid, p-value, study)

    Will delete all entries of triples for the file and study that is given
    Useful to delete a whole study, i.e. if something went wrong during loading
"""

import time
import h5py
import numpy as np
from numpy import genfromtxt
import argparse

# Create my compound type triple to be stored in the hash_table
vlen = h5py.special_dtype(vlen=str)
dt = np.dtype([("snp", vlen), ("pval", np.float32), ("chr", np.int), ("or", np.float32), ("study", vlen)])

def snp_hash(snp):
    # p is the first prime after the max number of characters I can get [a-zA-Z0-9] makes 62 unique characters
    p = 67

    # Map A -> 10 ... a -> 36 ... z -> 61
    SNP = [int(c) if c.isdigit() else ord(c) - ord('A') + 10 if c.islower() else ord(c) - ord('A') - 6 + 10 for c in snp]

    h = sum(pow(p, i) * s for i, s in enumerate(SNP))

    return h % N # MODULO


parser = argparse.ArgumentParser()
parser.add_argument('-tsv', help='The file to be loaded', required=True)
parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
parser.add_argument('-study', help='The name of the first group this will belong to', required=True)
args = parser.parse_args()

csvf = args.tsv
h5file = args.h5file
study = args.study

print(time.strftime('%a %H:%M:%S'))

snparray = genfromtxt(csvf, delimiter='\t', usecols=(0), dtype=object)
pvalarray = genfromtxt(csvf, delimiter='\t', usecols=(1), dtype = float)
chrarray = genfromtxt(csvf, delimiter = '\t', usecols = (2), dtype = int)
orarray = genfromtxt(csvf, delimiter = '\t', usecols = (3), dtype = float)


f = h5py.File(h5file, 'a')

dataset = f.get("hash_table")

N = dataset.shape[0]
print dataset.shape
emptydt = (None, 0., 0, 0., None)
for i in xrange(0, len(snparray)):
    snp = snparray[i]
    pval = pvalarray[i]
    chr = chrarray[i]
    or_val = orarray[i]

    snp_h = snp_hash(snp)
    array = dataset[snp_h]

    info_array = array[array["snp"] == snp]
    info_array = info_array[info_array["study"] == study]
    info_array = info_array[info_array["chr"] == chr]
    info_array = info_array[info_array["or"] == or_val]
    info_array = info_array[info_array["pval"] == pval]
    if info_array:
        element = info_array[0]

        for i in range(0, len(array)):
            if array[i]["snp"] == element["snp"] and \
                array[i]["study"] == element["study"] and \
                array[i]["chr"] == element["chr"] and \
                array[i]["or"] == element["or"] and \
                array[i]["pval"] == element["pval"]:

                array[i] = emptydt
        dataset[snp_h] = array



