"""
    Stores the data in the hierarchy of Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    snparray will hold the snp ids
    pvals will hold each snps pvalue for this study
    chr will hold each snps position
    or_array will hold each snps odds ratio for this study
    we can add any other information that we want

    the positions in the vectors correspond to each other
    snparray[0], pvals[0], chr[0], and or_array[0] hold the information for SNP 0

"""


import argparse
import time
from sumstats.utils import utils
import pandas as pd
from sumstats.trait.constants import *
import sumstats.utils.group_utils as gu
import numpy as np


def create_trait_group(file, trait):
    if trait in file:
        return gu.get_group_from_parent(file, trait)
    else:
        return file.create_group(trait)


def create_study_group(trait_group, study):
    if study in trait_group:
        return gu.get_group_from_parent(trait_group, study)
    else:
        return trait_group.create_group(study)


def create_dataset(group, dset_name, data):
    """
    :param data: a np.array of data elements (string, int, float)
    """
    data = np.array(data, dtype=DSET_TYPES[dset_name])
    group.create_dataset(dset_name, data=data, compression="gzip")


class Loader():

    def __init__(self, tsv, h5file, study, trait, dict_of_data=None):
        self.h5file = h5file
        self.study = study
        self.trait = trait

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

        self.name_to_dataset = utils.create_dataset_objects(name_to_list)

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