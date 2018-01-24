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


class Loader():

    def __init__(self, tsv, h5file, study, trait, dict_of_data=None):
        h5file = h5file
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

        self.datasets = utils.create_datasets_from_lists(name_to_list)

        # Open the file with read/write permissions and create if it doesn't exist
        self.file = h5py.File(h5file, 'a')

    def load(self):

        datasets = self.datasets

        trait_group = self._create_trait_group()
        study_group = self._create_study_group(trait_group)

        # group, dset_name, data
        for dset_name in TO_STORE_DSETS:
            gu.create_dataset(study_group, dset_name, datasets[dset_name])
            # flush after saving each dataset
            self.file.flush()

    def _create_trait_group(self):
        return gu.create_group_from_parent(self.file, self.trait)

    def _create_study_group(self, trait_group):
        if gu.subgroup_exists(trait_group, self.study):
            self.close_file()
            raise ValueError("This study has already been loaded! Study:", self.study)
        return gu.create_group_from_parent(trait_group, self.study)

    def close_file(self):
        self.file.close()


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
    loader.close_file()


if __name__ == '__main__':
    main()