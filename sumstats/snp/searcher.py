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

    Query: query for specific SNP that belongs

    Can filter based on p-value thresholds and/or specific study
"""

import sumstats.snp.query as query
import sumstats.utils.group as gu
import h5py
import sumstats.utils.restrictions as rst


class Search:

    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}

    def snp_in_file(self, snp):
        return snp in self.file

    def query_for_snp(self, snp, start, size):
        snp_group = gu.get_group_from_parent(self.file, snp)
        self.datasets = query.get_dsets_from_group(snp_group, start, size)

    def apply_restrictions(self, snp=None, study=None, chr=None, pval_interval=None, bp_interval=None):
        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chr, pval_interval, bp_interval)

    def get_result(self):
        return self.datasets

    def close_file(self):
        self.file.close()