"""
    Stored as /CHR/BLOCK/SNP/DATA
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

    Query 1: query for chromosome if bp thresholds are omitted
    or chromosome block if bp upper and lower limits are given
    Query 2: query for specific SNP that belongs to a chromosome

    Can filter based on p-value thresholds, bp position thresholds, and specific study
"""

import sumstats.chr.query_utils as myutils
import time
from sumstats.utils.restrictions import *
from sumstats.chr.constants import *
import sumstats.utils.group as gu
import sumstats.utils.utils as utils


def query_for_chromosome(chr_group):
    all_chr_block_groups = gu.get_all_groups_from_parent(chr_group)
    print("block size", len(all_chr_block_groups))
    return myutils.get_dsets_from_plethora_of_blocks(all_chr_block_groups)


def query_for_block_range(chr_group, block_lower_limit, block_upper_limit):
    filter_block_ceil = None
    filter_block_floor = None
    # for block size 100, if I say I want BP range 250 - 350 that means
    # I need to search for block 300 (200-300) and block 400 (300-400)

    from_block = myutils.get_block_number(block_lower_limit)
    to_block = myutils.get_block_number(block_upper_limit)

    block_groups = myutils.get_block_groups_from_parent_within_block_range(chr_group, from_block, to_block)

    # we might need to filter further if they don't fit exactly
    # e.g. we got the snps for range 200-400 now we need to filter 250-350
    if from_block != block_lower_limit:
        filter_block_floor = block_lower_limit
    if to_block != block_upper_limit:
        filter_block_ceil = block_upper_limit

    name_to_dataset = myutils.get_dsets_from_plethora_of_blocks(block_groups)
    bp_mask = name_to_dataset[BP_DSET].interval_mask(filter_block_floor, filter_block_ceil)

    if bp_mask is not None:
        name_to_dataset = utils.filter_dictionary_by_mask(name_to_dataset, bp_mask)

    return name_to_dataset


def query_for_snp(chr_group, block_number, snp):
    block_group = gu.get_group_from_parent(chr_group, block_number)
    snp_group = gu.get_group_from_parent(block_group, snp)

    return myutils.get_dsets_from_group(snp, snp_group)


def find_snp_in_group_name(name, group):
    if snp in name:
        return group.name


def find_snp_block(chr_group):
    group_name = chr_group.visititems(find_snp_in_group_name)
    name_array = group_name.split("/")
    return name_array[2]


def get_block_that_snp_belongs_to(chr_group, block_upper_limit):
    if block_upper_limit is None:
        snp_block = find_snp_block(chr_group)
    else:
        snp_block = myutils.get_block_number(block_upper_limit)
    return snp_block


def main():
    global snp
    myutils.argument_checker()
    args = myutils.argument_parser()

    # read the arguments correctly
    chr, query, block_upper_limit, block_lower_limit, snp, study, p_upper_limit, p_lower_limit = myutils.convert_args(args)

    # open h5 file in read mode
    f = h5py.File(args.h5file, mode="r")

    chr_group = gu.get_group_from_parent(f, chr)
    name_to_dataset = {}

    if query == 1:
        if block_lower_limit is None and block_upper_limit is None:
            print("Start querying for whole chromosome info")
            print(time.strftime('%a %H:%M:%S'))
            name_to_dataset = query_for_chromosome(chr_group)
            print("Done querying for whole chromosome info")
            print(time.strftime('%a %H:%M:%S'))
        else:
            if block_lower_limit is None:
                block_lower_limit = block_upper_limit
            elif block_upper_limit is None:
                block_upper_limit = block_lower_limit

            name_to_dataset = query_for_block_range(chr_group, block_lower_limit,
                                                    block_upper_limit)

    elif query == 2:
        snp_block_number = get_block_that_snp_belongs_to(chr_group, block_upper_limit)
        name_to_dataset = query_for_snp(chr_group, snp_block_number, snp)

    restrictions = []
    if study is not None:
        restrictions.append(EqualityRestriction(study, name_to_dataset[STUDY_DSET]))
    if p_upper_limit is not None or p_lower_limit is not None:
        restrictions.append(IntervalRestriction(p_lower_limit, p_upper_limit, name_to_dataset[MANTISSA_DSET]))

    if restrictions:
        name_to_dataset = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)

    print("Number of snp's retrieved", len(name_to_dataset[SNP_DSET]))
    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset][:10])


if __name__ == "__main__":
    main()