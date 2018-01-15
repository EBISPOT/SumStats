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

import sumstats.chr.query as query
import sumstats.utils.group as gu
import sumstats.utils.utils as utils
from sumstats.utils.interval import *
from sumstats.chr.constants import *
import sumstats.utils.restrictions as rst
import h5py


def fill_in_block_limits(bp_interval):
    if bp_interval.floor() is None:
        return IntInterval().set_tuple(bp_interval.ceil(), bp_interval.ceil())
    elif bp_interval.ceil() is None:
        return IntInterval().set_tuple(bp_interval.floor(), bp_interval.floor())
    else:
        return bp_interval


class Search():
    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}

    def query_for_chromosome(self, chromosome, start, size):
        chr_group = gu.get_group_from_parent(self.file, chromosome)

        all_chr_block_groups = gu.get_all_subgroups(chr_group)
        print("block size", len(all_chr_block_groups))
        self.datasets = query.get_dsets_from_plethora_of_blocks(all_chr_block_groups, start, size)

    def query_chr_for_block_range(self, chromosome, bp_interval, start, size):

        chr_group = gu.get_group_from_parent(self.file, chromosome)
        bp_interval = fill_in_block_limits(bp_interval)

        filter_block_ceil = None
        filter_block_floor = None
        # for block size 100, if I say I want BP range 250 - 350 that means
        # I need to search for block 300 (200-300) and block 400 (300-400)

        from_block = query.get_block_number(bp_interval.floor())
        to_block = query.get_block_number(bp_interval.ceil())

        block_interval = IntInterval().set_tuple(from_block, to_block)
        block_groups = query.get_block_groups_from_parent_within_block_range(chr_group, block_interval)

        # we might need to filter further if they don't fit exactly
        # e.g. we got the snps for range 200-400 now we need to filter 250-350
        if block_interval.floor() != bp_interval.floor():
            filter_block_floor = bp_interval.floor()
        if block_interval.ceil() != bp_interval.ceil():
            filter_block_ceil = bp_interval.ceil()

        datasets = query.get_dsets_from_plethora_of_blocks(block_groups, start, size)
        bp_mask = datasets[BP_DSET].interval_mask(filter_block_floor, filter_block_ceil)

        if bp_mask is not None:
            datasets = utils.filter_dictionary_by_mask(datasets, bp_mask)

        self.datasets = datasets

    def apply_restrictions(self, snp=None, study=None, chr=None, pval_interval=None, bp_interval=None):
        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chr, pval_interval, bp_interval)

    def get_result(self):
        return self.datasets

    def close_file(self):
        self.file.close()
