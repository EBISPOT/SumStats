"""
    Database design looks like:
    a 2D array where each element is a triple: (SNPid, p-value, study)

    It only makes sense to query for all the info about a SNP
    (or all the info about a chromosome especially if we split the snps into chromosome groups!)
    Can filter afterwords by study and or chromosome
    Can apply thresholds to p-value
"""


import h5py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-h5file', help = 'The name of the HDF5 file to be created/updated', required=True)
parser.add_argument('-snp', help = 'The SNP I am looking for')
parser.add_argument('-chr', help='The chromosome I am looking for')
parser.add_argument('-study', help='The study I am looking for')
parser.add_argument('-under', help='p-value under this threshold')
parser.add_argument('-over', help='p-value under this threshold')
args = parser.parse_args()

h5file = args.h5file
snp = args.snp
chr = args.chr
study = args.study
under = args.under
over = args.over

f = h5py.File(h5file, 'r')


def snp_hash(snp):
    # p is the first prime after the max number of characters I can get [a-zA-Z0-9] makes 62 unique characters
    p = 67

    # Map A -> 10 ... a -> 36 ... z -> 61
    SNP = [int(c) if c.isdigit() else ord(c) - ord('A') + 10 if c.islower() else ord(c) - ord('A') - 6 + 10 for c in snp]

    h = sum(pow(p, i) * s for i, s in enumerate(SNP))

    return h % N # MODULO


dataset = f.get("hash_table")
N = dataset.shape[0]
print dataset.shape
snp_h = snp_hash(snp)
print "snp_h is: %s" % (snp_h)

# get all the elements that exist in this bucket/row
array = dataset[snp_h]

# filter the chromosome we want
if chr is not None:
    info_array = array[array["chr"] == chr]

# filter the SNP we want
if snp is not None:
    info_array = array[array["snp"] == snp]

# filter the study if it is specified
if study is not None:
    info_array = info_array[info_array["study"] == study]

# filter p-value threshold if specified
if over is not None:
    info_array = info_array[info_array["pval"] >= float(over)]

if under is not None:
    info_array = info_array[info_array["pval"] <= float(under)]

print info_array
