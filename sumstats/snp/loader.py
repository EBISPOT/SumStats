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

import sumstats.utils.fileload as fl
from sumstats.snp.constants import *
import sumstats.snp.constants as const
import sumstats.utils.group as gu


class Loader:
    def __init__(self, tsv, h5file, study, dict_of_data=None):
        self.study = study

        datasets_as_lists = fl.read_datasets_from_input(tsv, dict_of_data, const)
        self.datasets = fl.format_datasets(datasets_as_lists, study, const)

        # Open the file with read/write permissions and create if it doesn't exist
        self.file = h5py.File(h5file, 'a')

    def load(self):
        if self.is_loaded():
            self.close_file()
            raise ValueError("This study has already been loaded! Study:", self.study)
        self._save_info_in_file()

    def is_loaded(self):
        datasets = self.datasets
        snps = datasets[SNP_DSET]
        first_snp = snps[0]
        last_snp = snps[-1]

        first_snp_loaded = self.snp_loaded_with_study(first_snp)
        last_snp_loaded = self.snp_loaded_with_study(last_snp)

        # true iff one is true and other is false (xor)
        if first_snp_loaded ^ last_snp_loaded:
            raise RuntimeError("Study is half loaded! Study:", self.study)
        else:
            return first_snp_loaded and last_snp_loaded

    def snp_loaded_with_study(self, snp):
        if snp not in self.file:
            return False

        snp_group = gu.create_group_from_parent(self.file, snp)
        return gu.value_in_dataset(snp_group, self.study, STUDY_DSET)

    def close_file(self):
        self.file.close()

    def _save_info_in_file(self):
        datasets = self.datasets
        snps = datasets[SNP_DSET]

        for i in range(len(snps)):
            self._save_snp(snps[i], i)

    def _save_snp(self, snp, snp_index):

        snp_group = gu.create_group_from_parent(self.file, snp)

        for dset_name in TO_STORE_DSETS:
            data_point = self.datasets[dset_name][snp_index]
            gu.expand_dataset(snp_group, dset_name, [data_point])


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
