"""
    Stored as /SNP/DATA
    Where DATA:
    under each directory we store 3 (or more) vectors
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

import sumstats.utils.fileload as fl
from sumstats.snp.constants import *
import sumstats.snp.constants as const
import sumstats.utils.group as gu
from sumstats.errors.error_classes import *
import sqlite3
from sumstats.utils.sqlite_client import sqlClient


class Loader:
    def __init__(self, tsv, h5file, study, database, dict_of_data=None):
        self.study = study
        self.database = database

        datasets_as_lists = fl.read_datasets_from_input(tsv, dict_of_data, const)
        self.datasets = fl.format_datasets(datasets_as_lists, study, const)

        # Open the file with read/write permissions and create if it doesn't exist
        #self.file = h5py.File(h5file, 'a')
        #self.file_group = gu.Group(self.file)

    def load(self):
        sqlcl = sqlClient(database=self.database)
        print('starting load...')
        print('database: {}'.format(self.database))
        try:
            sqlcl.drop_rsid_index()
        except sqlite3.OperationalError as e:
            print(e)
        for index, snp in enumerate(self.datasets[SNP_DSET]):
            data = (snp, self.datasets[CHR_DSET][index], self.datasets[BP_DSET][index])
            sqlcl.insert_snp_row(data)
        sqlcl.create_rsid_index()


#        if self.is_loaded():
#            self.close_file()
#            raise AlreadyLoadedError(self.study)
#        self._save_info_in_file()

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

        self.file_group.create_subgroup(snp)
        snp_group = self.file_group.get_subgroup(snp)

        return snp_group.subgroup_exists(self.study)
        #return snp_group.is_value_in_dataset(self.study, STUDY_DSET)

    def close_file(self):
        self.file.close()

    def _save_info_in_file(self):
        datasets = self.datasets
        snps = datasets[SNP_DSET]

        for i, snp in enumerate(snps):
            self._save_snp(snp, i)

    def _save_snp(self, snp, snp_index):
        snp_study = "/".join([str(snp), str(self.study)])

        self.file_group.create_subgroup(snp_study)
        snp_study_group = self.file_group.get_subgroup(snp_study)

        for dset_name in TO_STORE_DSETS:
            data_point = self.datasets[dset_name][snp_index]
            snp_study_group.expand_dataset(dset_name, [data_point])
