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
from sumstats.snp.constants import *
import sumstats.utils.group as gu


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


def save_info_in_file(file, name_to_dataset):
    snps = name_to_dataset[SNP_DSET]

    for i in range(len(snps)):
        snp = snps[i]
        if snp in file:
            snp_group = gu.get_group_from_parent(file, snp)
            for dset_name in TO_STORE_DSETS:
                expand_dataset(snp_group, dset_name, name_to_dataset[dset_name][i])
                # flush file after writing to prevent data corruption
                file.flush()
        else:
            snp_group = file.create_group(snp)
            for dset_name in TO_STORE_DSETS:
                create_dataset(snp_group, dset_name, name_to_dataset[dset_name][i])
                # flush file after writing to prevent data corruption
                file.flush()


class Loader():
    def __init__(self, tsv, h5file, study, dict_of_data=None):
        self.study = study

        if tsv is not None:
            name_to_list = {}
            assert dict_of_data is None, "dic_of_data is ignored"
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

        name_to_list[STUDY_DSET] = create_study_list(study, len(name_to_list[MANTISSA_DSET]))
        utils.assert_datasets_not_empty(name_to_list)

        self.name_to_dataset = utils.create_datasets_from_lists(name_to_list)
        # Open the file with read/write permissions and create if it doesn't exist
        self.file = h5py.File(h5file, 'a')

    def load(self):
        if self.already_loaded():
            raise ValueError("This study has already been loaded! Study:", self.study)
        name_to_dataset = self.name_to_dataset
        save_info_in_file(self.file, name_to_dataset)

    def already_loaded(self):
        name_to_dataset = self.name_to_dataset
        study = self.study
        file = self.file

        snps = name_to_dataset[SNP_DSET]
        random_snp = snps[0]
        if random_snp not in file:
            return False
        snp_group = gu.get_group_from_parent(file, random_snp)
        return gu.already_loaded_in_group(snp_group, study, STUDY_DSET)

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
