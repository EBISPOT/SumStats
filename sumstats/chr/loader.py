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
import numpy as np
import pandas as pd

from sumstats.utils import utils
from sumstats.chr.constants import *
import sumstats.utils.group_utils as gu


def create_dataset(group, dset_name, data):
    """
    Datasets with maxshape = ((None,)) so they can be extended
    max actual number of values we can store per array is 2^64 - 1
    data element needs to be converted to np.array first, otherwise it will
    be saved as a scalar, and won't be able to be extended later on into an array

    :param data: a single data element (string, int, float)
    """
    data = np.array([data], dtype=DSET_TYPES[dset_name])
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


def create_study_list(study, length_of):
    return [study for _ in range(length_of)]


def create_groups_in_parent(parent, list_of_groups):
    for new_group in list_of_groups:
        if str(new_group) not in parent:
            parent.create_group(str(new_group))


def slice_datasets_where_chromosome(chromosome, name_to_dataset):
    # get the slices from all the arrays where chromosome position == i
    chr_mask = name_to_dataset[CHR_DSET].equality_mask(chromosome)
    return utils.filter_dictionary_by_mask(name_to_dataset, chr_mask)


def initialize_block_limits():
    block_floor = 0
    block_ceil = BLOCK_SIZE
    return block_floor, block_ceil


def increment_block_limits(block_ceil):
    block_floor = block_ceil + 1
    block_ceil += BLOCK_SIZE
    return block_floor, block_ceil


def get_block_group_from_block_ceil(chr_group, block_ceil):
    block_group = chr_group.get(str(block_ceil))
    if block_group is None:
        block_group = chr_group.create_group(str(block_ceil))
    return block_group


def save_info_in_block_group(block_group, name_to_dataset):
    # for the block_group, loop through the snps
    # and save x arrays, one for each piece of information
    # in the corresponding position so the informaiton is kept in sync
    # i.e. snp[i] is saved in the 'snps' dataset in the same position as it's corresponding orvals[i]
    snps = name_to_dataset[SNP_DSET]

    for i in range(len(snps)):
        snp = snps[i]
        if snp in block_group:
            snp_group = gu.get_group_from_parent(block_group, snp)
            for dset_name in TO_STORE_DSETS:
                expand_dataset(snp_group, dset_name, name_to_dataset[dset_name][i])
        else:
            snp_group = block_group.create_group(snp)
            for dset_name in TO_STORE_DSETS:
                create_dataset(snp_group, dset_name, name_to_dataset[dset_name][i])


def block_limit_not_reached_max(block_ceil, max_bp):
    return int(block_ceil) <= (int(max_bp) + int(BLOCK_SIZE))


class Loader():
    def __init__(self, tsv, h5file, study, dict_of_data=None):
        self.h5file = h5file
        self.study = study

        if tsv is not None:
            name_to_list = {}
            assert dict_of_data is None, "dic_of_data is ignored"
            print(time.strftime('%a %H:%M:%S'))
            for name in TO_LOAD_DSET_HEADERS:
                name_to_list[name] = pd.read_csv(tsv, dtype=DSET_TYPES[name], usecols=[name], delimiter="\t").to_dict(orient='list')[name]
            print("Loaded tsv file: ", tsv)
            print(time.strftime('%a %H:%M:%S'))
        else:
            name_to_list = dict_of_data

        pval_list = name_to_list[PVAL_DSET]

        mantissa_dset, exp_dset = utils.get_mantissa_and_exp_lists(pval_list)
        del name_to_list[PVAL_DSET]

        name_to_list[MANTISSA_DSET] = mantissa_dset
        name_to_list[EXP_DSET] = exp_dset

        name_to_list[STUDY_DSET] = create_study_list(study, len(name_to_list[MANTISSA_DSET]))
        utils.assert_datasets_not_empty(name_to_list)

        self.name_to_dataset = utils.create_dataset_objects(name_to_list)

    def load(self):
        # Open the file with read/write permissions and create if it doesn't exist
        f = h5py.File(self.h5file, 'a')
        name_to_dataset = self.name_to_dataset

        unique_chromosomes_in_file = set(name_to_dataset[CHR_DSET])
        chromosome_array = np.array([x for x in unique_chromosomes_in_file])
        create_groups_in_parent(f, chromosome_array)

        for chromosome in chromosome_array:
            chr_group = gu.get_group_from_parent(f, chromosome)

            dsets_sliced_by_chr = slice_datasets_where_chromosome(chromosome, name_to_dataset)

            bp_list_chr = dsets_sliced_by_chr[BP_DSET]
            max_bp = max(bp_list_chr)

            print("max base pair location in chromosome:", max_bp)

            block_floor, block_ceil = initialize_block_limits()

            while block_limit_not_reached_max(block_ceil, max_bp):
                block_group = get_block_group_from_block_ceil(chr_group, block_ceil)
                block_mask = dsets_sliced_by_chr[BP_DSET].interval_mask(block_floor, block_ceil)
                if np.any(block_mask):
                    dsets_block_slices = utils.filter_dictionary_by_mask(dsets_sliced_by_chr, block_mask)
                    save_info_in_block_group(block_group, dsets_block_slices)

                block_floor, block_ceil = increment_block_limits(block_ceil)


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
