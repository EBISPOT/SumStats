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

import sumstats.chr.query_utils as myutils
from sumstats.utils.restrictions import *
from sumstats.chr.constants import *
import sumstats.utils.group as gu
import sumstats.utils.utils as utils
from sumstats.utils.interval import *
import sumstats.utils.argument_utils as au


def fill_in_block_limits(bp_interval):
    if bp_interval.floor() is None:
        return IntInterval().set_tuple(bp_interval.ceil(), bp_interval.ceil())
    elif bp_interval.ceil() is None:
        return IntInterval().set_tuple(bp_interval.floor(), bp_interval.floor())
    else:
        return bp_interval


class Search():
    def __init__(self, h5file):
        self.h5file = h5file
        # Open the file with read permissions
        self.f = h5py.File(h5file, 'r')
        self.name_to_dset = {}

    def query_for_chromosome(self, chromosome):
        chr_group = gu.get_group_from_parent(self.f, chromosome)

        all_chr_block_groups = gu.get_all_groups_from_parent(chr_group)
        print("block size", len(all_chr_block_groups))
        self.name_to_dset = myutils.get_dsets_from_plethora_of_blocks(all_chr_block_groups)

    def query_chr_for_block_range(self, chromosome, bp_interval):

        chr_group = gu.get_group_from_parent(self.f, chromosome)
        bp_interval = fill_in_block_limits(bp_interval)

        filter_block_ceil = None
        filter_block_floor = None
        # for block size 100, if I say I want BP range 250 - 350 that means
        # I need to search for block 300 (200-300) and block 400 (300-400)

        from_block = myutils.get_block_number(bp_interval.floor())
        to_block = myutils.get_block_number(bp_interval.ceil())

        block_interval = IntInterval().set_tuple(from_block, to_block)
        block_groups = myutils.get_block_groups_from_parent_within_block_range(chr_group, block_interval)

        # we might need to filter further if they don't fit exactly
        # e.g. we got the snps for range 200-400 now we need to filter 250-350
        if block_interval.floor() != bp_interval.floor():
            filter_block_floor = bp_interval.floor()
        if block_interval.ceil() != bp_interval.ceil():
            filter_block_ceil = bp_interval.ceil()

        name_to_dset = myutils.get_dsets_from_plethora_of_blocks(block_groups)
        bp_mask = name_to_dset[BP_DSET].interval_mask(filter_block_floor, filter_block_ceil)

        if bp_mask is not None:
            name_to_dset = utils.filter_dictionary_by_mask(name_to_dset, bp_mask)

        self.name_to_dset = name_to_dset

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


def main():
    args = au.search_argument_parser()
    trait, study, chr, bp_interval, snp, pval_interval = au.convert_search_args(args)

    search = Search(args.h5file)

    if bp_interval is None:
        search.query_for_chromosome(chr)
    else:
        search.query_chr_for_block_range(chr, bp_interval)

    search.apply_restrictions(study=study, pval_interval=pval_interval)

    name_to_dataset = search.get_result()

    print("Number of snp's retrieved", len(name_to_dataset[SNP_DSET]))
    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset][:10])


if __name__ == "__main__":
    main()