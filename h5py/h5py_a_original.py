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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tsv', help='The file to be loaded', required=True)
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-study', help='The name of the first group this will belong to', required=True)
    # parser.add_argument('trait_name', help = 'The name of the trait the SNPs of this file are related to')
    args = parser.parse_args()

    tsv = args.tsv
    h5file = args.h5file
    study = args.study
    # trait = args.trait_name
    print(time.strftime('%a %H:%M:%S'))

    # snp id is a string, so dtype = None
    snparray = genfromtxt(tsv, delimiter='\t', usecols=(0), dtype=None)
    pvalarray = genfromtxt(tsv, delimiter='\t', usecols=(1), dtype=float)
    chrarray = genfromtxt(tsv, delimiter='\t', usecols=(2), dtype=int)
    orarray = genfromtxt(tsv, delimiter='\t', usecols=(3), dtype=float)
    bparray = genfromtxt(tsv, delimiter='\t', usecols=(4), dtype=int)
    effectarray = genfromtxt(tsv, delimiter='\t', usecols=(5), dtype=None)
    otherarray = genfromtxt(tsv, delimiter='\t', usecols=(6), dtype=None)

    print "Loaded csv file: ", tsv
    print(time.strftime('%a %H:%M:%S'))

    # Open the file with read/write permissions and create if it doesn't exist
    f = h5py.File(h5file, 'a')

    # if trait in f:
    #     trait_group = f[trait]
    # else:
    #     trait_group = f.create_group(trait)

    # for the trait, create a group for every chromosome

    for i in range(1, 22):
        if str(i) not in f:
            f.create_group(str(i))

    if "X" not in f:
        f.create_group("X")
    if "Y" not in f:
        f.create_group("Y")
    if "MT" not in f:
        f.create_group("MT")

    block_size = 100000
    for i in range(1, 2):
        print(time.strftime('%a %H:%M:%S'))
        print "Chromosome:", i
        # get the array slice where chromosome position == i
        # from that slice keep the first column, i.e. the snpvalues (we know the chromosome)
        chr_mask = [chrarray == i]
        pvals_tmp = pvalarray[chr_mask]
        snps_tmp = snparray[chr_mask]
        orvals_tmp = orarray[chr_mask]
        bp_tmp = bparray[chr_mask]
        effect_tmp = effectarray[chr_mask]
        other_tmp = otherarray[chr_mask]

        print(time.strftime('%a %H:%M:%S'))
        print "Filtered chromosome..."

        chrom_group = f[str(i)]

        if snps_tmp.size != 0:

            # separate by BP (Chromosome Position)
            # have sorted the file rows by BP position (numeric)
            # so the last bp in the bparray is the biggest one
            max_bp = bp_tmp[len(bp_tmp) - 1]
            block_i_floor = 0
            block_i_ceil = block_size
            block_i_mask_c = bp_tmp <= block_i_ceil
            block_i_mask_f = bp_tmp >= block_i_floor
            block_i_mask = [all(tup) for tup in zip(block_i_mask_c, block_i_mask_f)]
            bps = bp_tmp[block_i_mask]
            while block_i_ceil <= (max_bp + block_size):
                print(time.strftime('%a %H:%M:%S'))
                print "Loading block %s - %s..." % (block_i_floor, block_i_ceil)
                print len(bps)
                if len(bps) > 0:
                    print "LOADING"
                    snps = snps_tmp[block_i_mask]
                    pvals = pvals_tmp[block_i_mask]
                    orvals = orvals_tmp[block_i_mask]
                    effects = effect_tmp[block_i_mask]
                    others = other_tmp[block_i_mask]

                    block_group = chrom_group.get(str(block_i_ceil))
                    if block_group is None:
                        block_group = chrom_group.create_group(str(block_i_ceil))

                    save_info_in_block(block_group, study, snps, pvals, orvals, bps, effects, others)

                print(time.strftime('%a %H:%M:%S'))
                print "Block %s - %s is loaded..." % (block_i_floor, block_i_ceil)

                # increment block
                block_i_floor = block_i_ceil + 1
                block_i_ceil += block_size
                block_i_mask_c = bp_tmp <= block_i_ceil
                block_i_mask_f = bp_tmp >= block_i_floor
                block_i_mask = [all(tup) for tup in zip(block_i_mask_c, block_i_mask_f)]
                bps = bp_tmp[block_i_mask]


def save_info_in_block(block_group, study, snps, pvals, orvals, bps, effects, others):
    # print snps
    for j in xrange(len(snps)):

        if j % 100000 == 0:
            print "Loaded %s so far..." % (j)
            print(time.strftime('%a %H:%M:%S'))

        snp_group = block_group.get(snps[j])
        if snp_group is None:
            snp_group = block_group.create_group(snps[j])

            # creating the datasets with maxshape = ((None,)) so they can be extended
            # max actual number of values we can store per array is 2^64 - 1

            d = np.array([pvals[j]])
            snp_group.create_dataset('pvals', data=d, maxshape=(None,), compression="gzip")

            d = np.array([study])
            snp_group.create_dataset('studies', data=d, maxshape=(None,), compression="gzip")

            d = np.array([orvals[j]])
            snp_group.create_dataset('or', data=d, maxshape=(None,), compression="gzip")

            d = np.array([bps[j]])
            snp_group.create_dataset('bp', data=d, maxshape=(None,), compression="gzip")

            d = np.array([effects[j]])
            snp_group.create_dataset('effect', data=d, maxshape=(None,), compression="gzip")

            d = np.array([others[j]])
            snp_group.create_dataset('other', data=d, maxshape=(None,), compression="gzip")
        else:
            # reading the existing datasets and expanding them by 1
            # the expansion can happen once for every new file/study that we load
            pvals_dset = snp_group['pvals']
            studies_dset = snp_group['studies']
            or_dset = snp_group['or']
            bps_dset = snp_group['bp']
            effects_dset = snp_group['effect']
            others_dset = snp_group['other']

            pvals_dset.resize((pvals_dset.shape[0] + 1,))
            pvals_dset[-1] = pvals[j]

            studies_dset.resize((studies_dset.shape[0] + 1,))
            studies_dset[-1] = study

            or_dset.resize((or_dset.shape[0] + 1,))
            or_dset[-1] = orvals[j]

            bps_dset.resize((bps_dset.shape[0] + 1,))
            bps_dset[-1] = bps[j]

            effects_dset.resize((effects_dset.shape[0] + 1,))
            effects_dset[-1] = effects[j]

            others_dset.resize((others_dset.shape[0] + 1,))
            others_dset[-1] = others[j]


if __name__ == "__main__":
    main()
