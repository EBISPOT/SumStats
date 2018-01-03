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
from sumstats.snp.constants import *
import sumstats.utils.group as gu
import sumstats.utils.utils as utils


class Search():

    def __init__(self, h5file):
        self.h5file = h5file
        # Open the file with read permissions
        self.f = h5py.File(h5file, 'r')
        self.name_to_dset = {}

    def snp_in_file(self, snp):
        print("snp", snp)
        return snp in self.f

    def query_for_snp(self, snp, start, size):
        snp_group = gu.get_group_from_parent(self.f, snp)
        self.name_to_dset = query.get_dsets_from_group(snp_group, start, size)

    def apply_restrictions(self, snp=None, study=None, chr=None, pval_interval=None, bp_interval=None):
        restrict_dict = {}
        if SNP_DSET in self.name_to_dset:
            restrict_dict[SNP_DSET] = snp
        if STUDY_DSET in self.name_to_dset:
            restrict_dict[STUDY_DSET] = study
        if CHR_DSET in self.name_to_dset:
            restrict_dict[CHR_DSET] = chr
        if MANTISSA_DSET in self.name_to_dset:
            restrict_dict[MANTISSA_DSET] = pval_interval
        if BP_DSET in self.name_to_dset:
            restrict_dict[BP_DSET] = bp_interval

        restrictions = utils.create_restrictions(self.name_to_dset, restrict_dict)
        if restrictions:
            self.name_to_dset = utils.filter_dsets_with_restrictions(self.name_to_dset, restrictions)

    def get_result(self):
        return self.name_to_dset