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

    Query: a chromosome group for a specific block range.
    Block range may span across mutliple block groups and that needs to be taken into account.
    Block range may have an upper limit, a lower limit, or both.

"""

import sumstats.chr.block as bk
import sumstats.chr.search.access.repository as query
import sumstats.utils.group as gu
import sumstats.utils.restrictions as rst
import sumstats.utils.utils as utils
from sumstats.common_constants import *


class BlockService:
    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}
        self.file_group = gu.Group(self.file)

    def query(self, chromosome, bp_interval, start, size):
        chr_group = self.file_group.get_subgroup(chromosome)
        block = bk.Block(bp_interval)

        filter_block_ceil = None
        filter_block_floor = None
        # for block size 100, if I say I want BP range 250 - 350 that means
        # I need to search for block 300 (200-300) and block 400 (300-400)

        block_groups = block.get_block_groups_from_parent(chr_group)

        # we might need to filter further if they don't fit exactly
        # e.g. we got the snps for range 200-400 now we need to filter 250-350
        if block.floor_block != bp_interval.floor():
            filter_block_floor = bp_interval.floor()
        if block.ceil_block != bp_interval.ceil():
            filter_block_ceil = bp_interval.ceil()

        datasets = query.load_datasets_from_groups(block_groups, start, size)
        bp_mask = datasets[BP_DSET].interval_mask(filter_block_floor, filter_block_ceil)

        if bp_mask is not None:
            datasets = utils.filter_dictionary_by_mask(datasets, bp_mask)

        self.datasets = datasets

    def apply_restrictions(self, snp=None, study=None, chromosome=None, pval_interval=None, bp_interval=None):
        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chromosome, pval_interval, bp_interval)

    def get_result(self):
        return self.datasets

    def get_block_range_size(self, chromosome, bp_interval):
        chr_group = self.file_group.get_subgroup(chromosome)
        block = bk.Block(bp_interval)
        block_groups = block.get_block_groups_from_parent(chr_group)
        return sum(bp_group.get_max_group_size() for bp_group in block_groups)

    def close_file(self):
        self.file.close()
