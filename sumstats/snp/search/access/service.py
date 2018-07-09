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

    Query: query for specific SNP
"""

import h5py

import sumstats.snp.search.access.repository as repo
import sumstats.utils.group as gu
import sumstats.utils.restrictions as rst
from sumstats.errors.error_classes import *


class Service:

    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}
        self.file_group = gu.Group(self.file)
        self.snp_group = None

    def snp_in_file(self, snp):
        # return None if snp not found or set the snp_group
        try:
            self._get_snp_group(snp)
            return True
        except (SubgroupError, NotFoundError):
            return False

    def query(self, snp, start, size):
        snp_group = self._get_snp_group(snp)
        self.datasets = repo.get_dsets_from_group(snp_group, start, size)

    def apply_restrictions(self, snp=None, study=None, chromosome=None, pval_interval=None, bp_interval=None):
        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chromosome, pval_interval, bp_interval)

    def get_result(self):
        return self.datasets

    def get_snp_size(self, snp):
        snp_group = self._get_snp_group(snp)
        return snp_group.get_max_group_size()

    def _get_snp_group(self, snp):
        # caches the latest searched variant
        if self.snp_group is None or snp not in self.snp_group.get_name():
            self.snp_group = self.file_group.get_subgroup(snp)
        return self.snp_group

    def close_file(self):
        self.file.close()