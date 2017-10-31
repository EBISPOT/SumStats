"""
    Data is stored in the hierarchy of /Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    'snp' list will hold the snp ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'chr' list will hold the chromosome that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    snp[0], mantissa[0], exp[0], and chr[0] hold the information for SNP 0

"""

import time
from sumstats.utils import utils
import pandas as pd
from sumstats.trait.constants import *
import sumstats.utils.group as gu
import numpy as np
import argparse


def create_trait_group(file, trait):
    if trait in file:
        return gu.get_group_from_parent(file, trait)
    else:
        return file.create_group(trait)


def create_study_group(trait_group, study):
    if study in trait_group:
        raise ValueError("Study already exists for this trait!", study)
    else:
        return trait_group.create_group(study)


def create_dataset(group, dset_name, data):
    """
    :param data: a np.array of data elements (string, int, float)
    """
    if dset_name in group:
        raise ValueError("Dataset already exists in group!", dset_name, group)
    data = np.array(data, dtype=DSET_TYPES[dset_name])
    group.create_dataset(dset_name, data=data, compression="gzip")


class Loader():

    def __init__(self, tsv, h5file, study, trait, dict_of_data=None):
        self.h5file = h5file
        self.study = study
        self.trait = trait

        assert trait is not None, "You need to specify a trait with the trait loader!"

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

        utils.assert_datasets_not_empty(name_to_list)

        self.name_to_dataset = utils.create_datasets_from_lists(name_to_list)

    def load(self):

        h5file = self.h5file
        study = self.study
        trait = self.trait
        name_to_dataset = self.name_to_dataset

        # Open the file with read/write permissions and create if it doesn't exist
        f = h5py.File(h5file, 'a')

        trait_group = create_trait_group(f, trait)
        study_group = create_study_group(trait_group, study)

        # group, dset_name, data
        for dset_name in TO_STORE_DSETS:
            create_dataset(study_group, dset_name, name_to_dataset[dset_name])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tsv', help = 'The file to be loaded')
    parser.add_argument('-h5file', help = 'The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-study', help = 'The name of the first group this will belong to', required=True)
    parser.add_argument('-trait', help = 'The name of the trait the SNPs of this file are related to', required=True)
    args = parser.parse_args()

    tsv = args.tsv
    h5file = args.h5file
    study = args.study
    trait = args.trait

    loader = Loader(tsv, h5file, study, trait)
    loader.load()


if __name__ == '__main__':
    main()