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

import sumstats.chr.block as bk
import sumstats.chr.search.access.repository as query
import sumstats.utils.group as gu
import sumstats.utils.restrictions as rst
import sumstats.utils.dataset_utils as utils
from sumstats.common_constants import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class BlockService:
    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}
        self.file_group = gu.Group(self.file)

    def query(self, chromosome, bp_interval, start, size):
        logger.debug("Starting query for chromosome: %s, bp_interval: %s, start: %s, size: %s", str(chromosome),
                     str(bp_interval), str(start), str(size))
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
        logger.debug("Query for chromosome: %s, bp_interval: %s, start: %s, size: %s done...", str(chromosome),
                     str(bp_interval), str(start), str(size))
        self.datasets = datasets

    def apply_restrictions(self, snp=None, study=None, chromosome=None, pval_interval=None, bp_interval=None):
        logger.debug("Applying restrictions: snp %s, study %s, chromosome %s, pval_interval %s, bp_interval %s",
                     str(snp), str(study), str(chromosome), str(pval_interval), str(bp_interval))
        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chromosome, pval_interval, bp_interval)
        logger.debug("Applying restrictions: snp %s, study %s, chromosome %s, pval_interval %s, bp_interval %s done...",
                     str(snp), str(study), str(chromosome), str(pval_interval), str(bp_interval))

    def get_result(self):
        return self.datasets

    def get_block_range_size(self, chromosome, bp_interval):
        """
        For a bp interval we create the Block object which in turn returns the (Group object)
        block groups that belong to this interval. We then sum up the group sizes.
        :param chromosome: The chromosome number we are intereted in
        :param bp_interval: the bp_interval we are interested in (needs to be an IntInterval)
        :return: the total group size of the block range given
        """
        chr_group = self.file_group.get_subgroup(chromosome)
        block = bk.Block(bp_interval)
        block_groups = block.get_block_groups_from_parent(chr_group)
        size = sum(bp_group.get_max_group_size() for bp_group in block_groups)
        logger.debug("Size of block group in range: %s, %s is %s",
                     str(bp_interval.floor()), str(bp_interval.ceil()), size)
        return size

    def close_file(self):
        logger.debug("Closing file %s...", self.file.file)
        self.file.close()
