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
import time


def snp_hash(snp, N):
    # p is the first prime after the max number of characters I can get [a-zA-Z0-9] makes 62 unique characters
    p = 67

    # Map A -> 10 ... a -> 36 ... z -> 61
    SNP = [int(c) if c.isdigit() else ord(c) - ord('A') + 10 if c.islower() else ord(c) - ord('A') - 6 + 10 for c in
           snp]

    h = sum(pow(p, i) * s for i, s in enumerate(SNP))

    return h % N  # MODULO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-snp', help='The SNP I am looking for')
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

    if snp is not None:
        info_array = get_by_snp(f, snp)
    elif chr is not None:
        info_array = get_by_chr(f, chr)
    else:
       info_array = get_all(f)

    info_array = filter_by_study(info_array, study)

    info_array = filter_by_over(info_array, over)

    info_array = filter_by_under(info_array, under)

    print info_array


# filter the SNP we want
def get_by_snp(f, snp):
    dataset = f.get("hash_table")
    N = dataset.shape[0]
    print dataset.shape
    snp_h = snp_hash(snp, N)
    print "snp_h is: %s" % (snp_h)
    array = dataset[snp_h]
    info_array = array[array["snp"] == snp]
    return info_array


def get_by_chr(f, chr):
    dataset = f.get("hash_table")
    print(time.strftime('%a %H:%M:%S'))
    print "Starting to load whole dataset..."
    info_array = dataset[:]
    print "Loaded whole dataset done!"
    print(time.strftime('%a %H:%M:%S'))

    print "Filtering out chromosome starting..."
    print(time.strftime('%a %H:%M:%S'))
    info_array = info_array[info_array["chr"] == int(chr)]
    print(time.strftime('%a %H:%M:%S'))
    print "Filtering chromosome done!"
    return info_array


def get_all(f):
    dataset = f.get("hash_table")
    return  dataset[:]


def filter_by_study(array, study):
    # filter the study if it is specified
    if study is not None:
        array = array[array["study"] == study]
    return array


def filter_by_over(array, over):
    # filter p-value threshold if specified
    if over is not None:
        array = array[array["pval"] >= float(over)]
    return array


def filter_by_under(array, under):
    if under is not None:
        array = array[array["pval"] <= float(under)]
    return array