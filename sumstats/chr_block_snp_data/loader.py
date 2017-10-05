"""
    Stored as CHR/SNP/DATA
    Where DATA is:
    pvals: a vector that holds the p-values for this SNP/Trait association
    or: a vector that holds the OR value for this SNP/Trait association
    studies: a vector that holds the studies that correspond to the p-values for this SNP/Trait association

    can add more information if needed
"""

import argparse
import time

import h5py
import numpy as np
from numpy import genfromtxt

import sumstats.utils as utils


def create_dataset(group, dset_name, data):
    """
    Datasets with maxshape = ((None,)) so they can be extended
    max actual number of values we can store per array is 2^64 - 1
    data element needs to be converted to np.array first, otherwise it will
    be saved as a scalar, and won't be able to be extended later on into an array

    :param group: an hdf5 group
    :param dset_name: a string with the dataset name
    :param data: a single data element (string, int, float)
    """
    if type(data) is str or type(data) is np.str_:
        vlen = h5py.special_dtype(vlen=str)
        data = np.array([data], dtype=vlen)
        group.create_dataset(dset_name, data=data, maxshape=(None,), compression="gzip")
    else:
        data = np.array([data])
        group.create_dataset(dset_name, data=data, maxshape=(None,), compression="gzip")


def expand_dataset(group, dset_name, data):
    """
    Epands the dset_name dataset by 1 element (data)
    Resizes first by 1 element, and then saves the new data point in the last position

    :param group: and hdf5 group
    :param dset_name: a string with the dataset name
    :param data: a single data element (string, int, float)
    """
    dset = group.get(dset_name)
    if dset is None:
        create_dataset(group, dset_name, data)
    else:
        dset.resize((dset.shape[0] + 1,))
        dset[-1] = data


def create_chromosome_groups(f, array_of_chromosomes):
    for chr in array_of_chromosomes:
        if str(chr) not in f:
            f.create_group(str(chr))


def save_info_in_block(block_group, study, snps, pvals, orvals, bps, effects, others):
    # for the block_group, loop through the snps
    # and save x arrays, one for each piece of information
    # in the corresponding position so the informaiton is kept in sync
    # i.e. snp[i] is saved in the 'snps' dataset in the same position as it's corresponding orvals[i]
    for i in range(len(snps)):

        snp_group = block_group.get(snps[i])
        if snp_group is None:
            snp_group = block_group.create_group(snps[i])

            create_dataset(snp_group, 'pval', pvals[i])
            create_dataset(snp_group, 'study', study)
            create_dataset(snp_group, 'or', orvals[i])
            create_dataset(snp_group, 'bp', bps[i])
            create_dataset(snp_group, 'effect', effects[i])
            create_dataset(snp_group, 'other', others[i])
        else:
            # reading the existing datasets and expanding them by 1
            # the expansion can happen once for every new file/study that we load
            expand_dataset(snp_group, 'pval', pvals[i])
            expand_dataset(snp_group, 'study', study)
            expand_dataset(snp_group, 'or', orvals[i])
            expand_dataset(snp_group, 'bp', bps[i])
            expand_dataset(snp_group, 'effect', effects[i])
            expand_dataset(snp_group, 'other', others[i])


class Loader():
    def __init__(self, tsv, h5file, study, snp_array=None, pval_array=None, chr_array=None, or_array=None, bp_array=None,
                 effect_array=None, other_array=None):
        self.h5file = h5file
        self.study = study

        if tsv is None:
            loaded = False
            if snp_array is not None and pval_array is not None and chr_array is not None and or_array is not None and bp_array is not None and effect_array is not None and other_array is not None:
                if snp_array.size != 0 and pval_array.size != 0 and chr_array.size != 0 and or_array.size != 0 and bp_array.size != 0 and effect_array.size != 0 and other_array.size != 0:
                    loaded = True
                    self.snp_array = snp_array
                    self.pval_array = pval_array
                    self.chr_array = chr_array
                    self.or_array = or_array
                    self.bp_array = bp_array
                    self.effect_array = effect_array
                    self.other_array = other_array
            if not loaded:
                print("If no tsv file provided, the arrays containing the study info must not be empty or None")
                raise SystemExit(1)
        else:
            # trait = args.trait_name
            print(time.strftime('%a %H:%M:%S'))

            # snp id is a string, so dtype = None
            # will be ndarrays
            self.snp_array = genfromtxt(tsv, delimiter='\t', usecols=(0), dtype=None)
            self.pval_array = genfromtxt(tsv, delimiter='\t', usecols=(1), dtype=float)
            self.chr_array = genfromtxt(tsv, delimiter='\t', usecols=(2), dtype=int)
            self.or_array = genfromtxt(tsv, delimiter='\t', usecols=(3), dtype=float)
            self.bp_array = genfromtxt(tsv, delimiter='\t', usecols=(4), dtype=int)
            self.effect_array = genfromtxt(tsv, delimiter='\t', usecols=(5), dtype=None)
            self.other_array = genfromtxt(tsv, delimiter='\t', usecols=(6), dtype=None)

            print("Loaded tsv file: ", tsv)
            print(time.strftime('%a %H:%M:%S'))

    def load(self):
        # Open the file with read/write permissions and create if it doesn't exist
        f = h5py.File(self.h5file, 'a')

        chromosome_array = [i for i in range(1, 23)]
        chromosome_array = np.array(chromosome_array)

        create_chromosome_groups(f, chromosome_array)

        study = self.study
        block_size = 100000
        for chromosome in chromosome_array:
            # print(time.strftime('%a %H:%M:%S'))
            # print("Chromosome:", chromosome
            # get the slices from all the arrays where chromosome position == i
            chr_mask = utils.get_equality_mask(chromosome, self.chr_array)
            snps_chr = utils.filter_by_mask(self.snp_array, chr_mask)
            pvals_chr = utils.filter_by_mask(self.pval_array, chr_mask)
            orvals_chr = utils.filter_by_mask(self.or_array, chr_mask)
            bp_chr = utils.filter_by_mask(self.bp_array, chr_mask)
            effect_chr = utils.filter_by_mask(self.effect_array, chr_mask)
            other_chr = utils.filter_by_mask(self.other_array, chr_mask)

            # print(time.strftime('%a %H:%M:%S'))
            # print("Filtered chromosome..."

            chrom_group = utils.get_group_from_parent(f, chromosome)
            if snps_chr.size > 0:
                # Filter by BP (Chromosome Position)
                max_bp = max(bp_chr)
                print("MAX OF ARRAY:", max_bp)
                block_i_floor = 0
                block_i_ceil = block_size
                block_i_mask = utils.cutoff_mask(bp_chr, block_i_ceil, block_i_floor)
                bps = utils.filter_by_mask(bp_chr, block_i_mask)

                while block_i_ceil <= (max_bp + block_size):
                    # print(time.strftime('%a %H:%M:%S')))
                    # print("Loading block %s - %s..." % (block_i_floor, block_i_ceil))

                    if len(bps) > 0:
                        # filter the info that we want based on the block mask
                        snps = utils.filter_by_mask(snps_chr, block_i_mask)
                        pvals = utils.filter_by_mask(pvals_chr, block_i_mask)
                        orvals = utils.filter_by_mask(orvals_chr, block_i_mask)
                        effects = utils.filter_by_mask(effect_chr, block_i_mask)
                        others = utils.filter_by_mask(other_chr, block_i_mask)

                        # if the block doesn't exist in the chromosome group, create it
                        block_group = chrom_group.get(str(block_i_ceil))
                        if block_group is None:
                            block_group = chrom_group.create_group(str(block_i_ceil))

                        save_info_in_block(block_group, study, snps, pvals, orvals, bps, effects, others)

                    # print(time.strftime('%a %H:%M:%S')))
                    # print("Block %s - %s is loaded..." % (block_i_floor, block_i_ceil))

                    # increment block
                    block_i_floor = block_i_ceil + 1
                    block_i_ceil += block_size
                    block_i_mask = utils.cutoff_mask(bp_chr, block_i_ceil, block_i_floor)
                    bps = utils.filter_by_mask(bp_chr, block_i_mask)


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

    loader = Loader(tsv, h5file, study)
    loader.load()


if __name__ == "__main__":
    main()
