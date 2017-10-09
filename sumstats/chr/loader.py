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
import pandas as pd

from sumstats.utils import utils

TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr', 'or', 'bp', 'effect', 'other']
TO_STORE_DSETS = ['pval', 'or', 'bp', 'effect', 'other']
BLOCK_SIZE = 100000
SNP_DSET = 'snp'
BP_DSET = 'bp'
PVAL_DSET = 'pval'
CHR_DSET = 'chr'
STUDY_DSET = 'study'


def create_dataset(group, dset_name, data):
    """
    Datasets with maxshape = ((None,)) so they can be extended
    max actual number of values we can store per array is 2^64 - 1
    data element needs to be converted to np.array first, otherwise it will
    be saved as a scalar, and won't be able to be extended later on into an array

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

    :param data: a single data element (string, int, float)
    """
    dset = group.get(dset_name)
    if dset is None:
        create_dataset(group, dset_name, data)
    else:
        dset.resize((dset.shape[0] + 1,))
        dset[-1] = data


def create_groups_in_parent(parent, list_of_groups):
    for new_group in list_of_groups:
        if str(new_group) not in parent:
            parent.create_group(str(new_group))


def slice_datasets_where_chromosome(chromosome, dict_of_dsets):
    # get the slices from all the arrays where chromosome position == i
    chr_mask = utils.get_equality_mask(chromosome, dict_of_dsets[CHR_DSET])
    return utils.filter_dictionary_by_mask(dict_of_dsets, chr_mask)


def initialize_block_limits():
    block_floor = 0
    block_ceil = BLOCK_SIZE
    return block_floor, block_ceil


def increment_block_limits(block_floor, block_ceil):
    block_floor = block_ceil + 1
    block_ceil += BLOCK_SIZE
    return block_floor, block_ceil


def get_block_group_from_block_ceil(chr_group, block_ceil):
    block_group = chr_group.get(str(block_ceil))
    if block_group is None:
        block_group = chr_group.create_group(str(block_ceil))
    return block_group


def save_info_in_block_group(block_group, study, dict_of_dsets):
    # for the block_group, loop through the snps
    # and save x arrays, one for each piece of information
    # in the corresponding position so the informaiton is kept in sync
    # i.e. snp[i] is saved in the 'snps' dataset in the same position as it's corresponding orvals[i]
    snps = dict_of_dsets[SNP_DSET]

    for i in range(len(snps)):
        snp = snps[i]
        if snp in block_group:
            snp_group = utils.get_group_from_parent(block_group, snp)
            for dset_name in TO_STORE_DSETS:
                expand_dataset(snp_group, dset_name, dict_of_dsets[dset_name][i])
            # expand study dataset
            expand_dataset(snp_group, STUDY_DSET, study)
        else:
            snp_group = block_group.create_group(snp)
            for dset_name in TO_STORE_DSETS:
                create_dataset(snp_group, dset_name, dict_of_dsets[dset_name][i])
                # create the study dataset
            create_dataset(snp_group, STUDY_DSET, study)


def block_limit_not_reached_max(block_ceil, max_bp):
    return block_ceil <= (max_bp + BLOCK_SIZE)


class Loader():
    def __init__(self, tsv, h5file, study, dictionary_of_dsets=None):
        self.h5file = h5file
        self.study = study
        self.dictionary_of_dsets = dictionary_of_dsets

        if tsv is None:
            utils.convert_lists_to_np_arrays(dictionary_of_dsets)
        else:
            print(time.strftime('%a %H:%M:%S'))

            dictionary_of_dsets = pd.read_csv(tsv, names=TO_LOAD_DSET_HEADERS, delimiter="\t").to_dict(orient='list')
            utils.check_correct_headers(dictionary_of_dsets, TO_LOAD_DSET_HEADERS)

            print("Loaded tsv file: ", tsv)
            print(time.strftime('%a %H:%M:%S'))

        utils.evaluate_datasets(dictionary_of_dsets)

    def load(self):
        # Open the file with read/write permissions and create if it doesn't exist
        f = h5py.File(self.h5file, 'a')
        dict_of_dsets = self.dictionary_of_dsets
        study = self.study

        unique_chromosomes_in_file = set(dict_of_dsets[CHR_DSET])
        chromosome_array = np.array([x for x in iter(unique_chromosomes_in_file)])
        create_groups_in_parent(f, chromosome_array)

        for chromosome in chromosome_array:
            dsets_chromosome_slices = slice_datasets_where_chromosome(chromosome, dict_of_dsets)

            chr_group = utils.get_group_from_parent(f, chromosome)
            bp_list_chr = dsets_chromosome_slices[BP_DSET]
            max_bp = max(bp_list_chr)

            print("max baise pair location in chromosome:", max_bp)

            block_floor, block_ceil = initialize_block_limits()

            while block_limit_not_reached_max(block_ceil, max_bp):

                block_mask = utils.cutoff_mask(bp_list_chr, block_floor, block_ceil)
                if np.any(block_mask):
                    dsets_block_slices = utils.filter_dictionary_by_mask(dsets_chromosome_slices, block_mask)
                    block_group = get_block_group_from_block_ceil(chr_group, block_ceil)
                    save_info_in_block_group(block_group, study, dsets_block_slices)

                block_floor, block_ceil = increment_block_limits(block_floor, block_ceil)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tsv', help='The file to be loaded', required=True)
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-study', help='The name of the first group this will belong to', required=True)
    args = parser.parse_args()

    tsv = args.tsv
    h5file = args.h5file
    study = args.study

    loader = Loader(tsv, h5file, study)
    loader.load()


if __name__ == "__main__":
    main()
