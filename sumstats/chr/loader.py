"""
    Stored as /CHR/BLOCK/SNP/DATA
    Where DATA:
    under each SNP directory we store 3 (or more) vectors
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'bp' list will hold the baise pair location that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    for a SNP group:
    study[0], mantissa[0], exp[0], and bp[0] hold the information for this SNP for study[0]
"""

import argparse
import time
import numpy as np
import pandas as pd

from sumstats.utils import utils
from sumstats.chr.constants import *
import sumstats.utils.group as gu
import sumstats.chr.query as query


def expand_dataset(group, dset_name, data):
    dset = group.get(dset_name)
    if dset is None:
        gu.create_dataset(group, dset_name, data)
    else:
        last_index_before_resize = dset.shape[0]
        dset.resize(((dset.shape[0] + len(data)),))
        dset[last_index_before_resize:] = data


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


def block_limit_not_reached_max(block_ceil, max_bp):
    return int(block_ceil) <= (int(max_bp) + int(BLOCK_SIZE))


def save_info_in_block_group(block_group, datasets):
    gu.check_group_dsets_shape(block_group, TO_STORE_DSETS)

    for dset_name in TO_STORE_DSETS:
        expand_dataset(block_group, dset_name, datasets[dset_name])


class Loader():
    def __init__(self, tsv, h5file, study, dict_of_data=None):
        self.study = study
        assert self.study is not None, "You need to specify a study accession"

        if tsv is not None:
            name_to_list = {}
            assert dict_of_data is None, "dict_of_data is ignored"
            print(time.strftime('%a %H:%M:%S'))
            for name in TO_LOAD_DSET_HEADERS:
                name_to_list[name] = \
                pd.read_csv(tsv, dtype=DSET_TYPES[name], usecols=[name], delimiter="\t").to_dict(orient='list')[name]
            print("Loaded tsv file: ", tsv)
            print(time.strftime('%a %H:%M:%S'))
        else:
            name_to_list = dict_of_data

        pval_list = name_to_list[PVAL_DSET]

        mantissa_dset, exp_dset = utils.get_mantissa_and_exp_lists(pval_list)
        del name_to_list[PVAL_DSET]

        name_to_list[MANTISSA_DSET] = mantissa_dset
        name_to_list[EXP_DSET] = exp_dset

        name_to_list[STUDY_DSET] = [study for _ in range(len(name_to_list[MANTISSA_DSET]))]
        utils.assert_datasets_not_empty(name_to_list)

        self.datasets = utils.create_datasets_from_lists(name_to_list)

        # Open the file with read/write permissions and create if it doesn't exist
        self.file = h5py.File(h5file, 'a')

    def load(self):
        if self._is_loaded():
            raise ValueError("This study has already been loaded! Study:", self.study)

        chromosome_array = self._get_chromosome_array()

        for chromosome in chromosome_array:
            self._save_chr_info_to_file(chromosome)

    def _is_loaded(self):
        first_chromosome = self.datasets[CHR_DSET][0]
        first_bp = self.datasets[BP_DSET][0]
        last_chromosome = self.datasets[CHR_DSET][-1]
        last_bp = self.datasets[BP_DSET][-1]

        first_bp_loaded = self._is_block_loaded_with_study(first_chromosome, first_bp)
        last_bp_loaded = self._is_block_loaded_with_study(last_chromosome, last_bp)

        if first_bp_loaded ^ last_bp_loaded:
            raise RuntimeError("Study is half loaded! Study:", self.study)
        return first_bp_loaded and last_bp_loaded

    def _is_block_loaded_with_study(self, chr, bp_position):
        chr = str(chr)
        block_number = query.get_block_number(bp_position)
        if not gu.subgroup_exists(self.file, chr):
            return False
        chr_group = gu.get_group_from_parent(self.file, chr)

        if not gu.subgroup_exists(chr_group, block_number):
            return False

        block_group = gu.get_group_from_parent(chr_group, block_number)
        return gu.value_in_dataset(block_group, self.study, STUDY_DSET)

    def _get_chromosome_array(self):
        datasets = self.datasets
        unique_chromosomes_in_file = set(datasets[CHR_DSET])
        return np.array([x for x in unique_chromosomes_in_file])

    def _save_chr_info_to_file(self, chromosome):
        print("Loading chromosome:", chromosome)
        chr_group = gu.create_group_from_parent(self.file, chromosome)
        dsets_sliced_by_chr = self._slice_datasets_where_chromosome(chromosome)

        self._save_block_info_to_file(chr_group, dsets_sliced_by_chr)

    def _slice_datasets_where_chromosome(self, chromosome):
        # get the slices from all the arrays where chromosome position == i
        chr_mask = self.datasets[CHR_DSET].equality_mask(chromosome)
        return utils.filter_dictionary_by_mask(self.datasets, chr_mask)

    def _save_block_info_to_file(self, chr_group, datasets):
        max_bp = self._max_bp_location(datasets)
        print("max base pair location in chromosome:", max_bp)

        block_floor, block_ceil = initialize_block_limits()

        while block_limit_not_reached_max(block_ceil, max_bp):
            block_group = get_block_group_from_block_ceil(chr_group, block_ceil)
            block_mask = datasets[BP_DSET].interval_mask(block_floor, block_ceil)
            if np.any(block_mask):
                dsets_block_slices = utils.filter_dictionary_by_mask(datasets, block_mask)
                save_info_in_block_group(block_group, dsets_block_slices)
                # flush file after writing to prevent data corruption
                self.file.flush()

            block_floor, block_ceil = increment_block_limits(block_ceil)

    def _max_bp_location(self, datasets):
        bp_list_chr = datasets[BP_DSET]
        return max(bp_list_chr)

    def close_file(self):
        self.file.close()


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
    loader.close_file()


if __name__ == "__main__":
    main()
