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
    group.create_dataset(dset_name, data=data, compression="gzip")


class Loader():

    def __init__(self, tsv, h5file, study, trait, dict_of_dsets=None):
        self.h5file = h5file
        self.study = study
        self.trait = trait

        if tsv is not None:
            assert dict_of_dsets is None, "dict_of_dsets is ignored"
            print(time.strftime('%a %H:%M:%S'))

            name_to_dataset = pd.read_csv(tsv, dtype=object, names=TO_LOAD_DSET_HEADERS, delimiter="\t").to_dict(orient='list')

            utils.remove_headers(name_to_dataset, TO_LOAD_DSET_HEADERS)
            print("Loaded tsv file: ", tsv)
            print(time.strftime('%a %H:%M:%S'))
        else:
            name_to_dataset = dict_of_dsets

        pval_dset = name_to_dataset[PVAL_DSET]
        mantissa_dset, exp_dset = utils.get_mantissa_and_exp_dsets(pval_dset)
        del name_to_dataset[PVAL_DSET]

        name_to_dataset[MANTISSA_DSET] = mantissa_dset
        name_to_dataset[EXP_DSET] = exp_dset

        name_to_dataset = utils.convert_lists_to_np_arrays(name_to_dataset, DSET_TYPES)
        utils.assert_np_datasets_not_empty(name_to_dataset)
        self.name_to_dataset = name_to_dataset

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