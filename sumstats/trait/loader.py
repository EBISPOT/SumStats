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


import h5py
import argparse
import time
import numpy as np
from sumstats.utils import utils
import pandas as pd

file_column_names = ['snp', 'pval', 'chr', 'or', 'bp', 'effect', 'other']
dataset_to_store_names = ['snp', 'pval', 'chr', 'or', 'bp', 'effect', 'other']


def create_trait_group(file, trait):
    if trait in file:
        return utils.get_group_from_parent(file, trait)
    else:
        return file.create_group(trait)


def create_study_group(trait_group, study):
    if study in trait_group:
        return utils.get_group_from_parent(trait_group, study)
    else:
        return trait_group.create_group(study)


def create_dataset(group, dset_name, data):
    """
    :param group: an hdf5 group
    :param dset_name: a string with the dataset name
    :param data: a np.array of data elements (string, int, float)
    """
    if np.issubdtype(data.dtype, str):
        vlen = h5py.special_dtype(vlen=str)
        data = np.array(data, dtype=vlen)
        group.create_dataset(dset_name, data=data, compression="gzip")
    else:
        group.create_dataset(dset_name, data=data, compression="gzip")


class Loader():

    def __init__(self, tsv, h5file, study, trait, dictionary_of_dsets=None):
        self.h5file = h5file
        self.study = study
        self.trait = trait
        self.dictionary_of_dsets = dictionary_of_dsets

        if tsv is None:
            utils.convert_lists_to_np_arrays(dictionary_of_dsets)
        else:
            print(time.strftime('%a %H:%M:%S'))

            dictionary_of_dsets = pd.read_csv(tsv, names=file_column_names, delimiter="\t").to_dict(orient='list')

            utils.check_correct_headers(dictionary_of_dsets, file_column_names)
            print("Loaded tsv file: ", tsv)
            print(time.strftime('%a %H:%M:%S'))

        utils.evaluate_datasets(dictionary_of_dsets)

    def load(self):

        h5file = self.h5file
        study = self.study
        trait = self.trait
        dictionary_of_dsets = self.dictionary_of_dsets

        # Open the file with read/write permissions and create if it doesn't exist
        f = h5py.File(h5file, 'a')

        trait_group = create_trait_group(f, trait)
        study_group = create_study_group(trait_group, study)

        # group, dset_name, data
        for dset_name in dataset_to_store_names:
            create_dataset(study_group, dset_name, dictionary_of_dsets[dset_name])


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