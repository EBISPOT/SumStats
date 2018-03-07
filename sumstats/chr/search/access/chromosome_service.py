"""
    Stored as /CHR/BLOCK/DATA
    Where DATA:
    under each directory we store 3 (or more) vectors
    'snp' list will hold the snp ids
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'bp' list will hold the baise pair location that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    snp[0], study[0], mantissa[0], exp[0], and bp[0] hold the information for this SNP for study[0]

    Query: query for chromosome if bp thresholds are omitted
    or chromosome block if bp upper and lower limits are given

    Can filter based on p-value thresholds, bp position thresholds, and specific study
"""

import sumstats.chr.search.access.repository as query
import sumstats.utils.group as gu
import sumstats.utils.restrictions as rst
from sumstats.common_constants import *


class ChromosomeService:
    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}
        self.file_group = gu.Group(self.file)

    def query(self, chromosome, start, size):
        chr_group = self.file_group.get_subgroup(chromosome)

        all_chr_sub_groups = chr_group.get_all_subgroups()
        self.datasets = query.load_datasets_from_groups(all_chr_sub_groups, start, size)

    def apply_restrictions(self, snp=None, study=None, chromosome=None, pval_interval=None, bp_interval=None):
        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chromosome, pval_interval, bp_interval)

    def get_result(self):
        return self.datasets

    def get_chromosome_size(self, chromosome):
        chromosome_group = self.file_group.get_subgroup(chromosome)
        return sum(bp_group.get_max_group_size() for bp_group in chromosome_group.get_all_subgroups())

    def close_file(self):
        self.file.close()
