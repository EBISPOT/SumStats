"""
    Stored as CHR/SNP/DATA
    Where DATA is:
    pvals: a vector that holds the p-values for this SNP/Trait association
    or: a vector that holds the OR value for this SNP/Trait association
    studies: a vector that holds the studies that correspond to the p-values for this SNP/Trait association

    Queries that make sense here is to query all information on a chromosome
    or all information on a SNP (if you have chromosome it will save an immense amount of time)
    And then filter by study(/trait) and/or by p-value threshold
"""

import sumstats.chr.query_utils as myutils
import time
from sumstats.utils.restrictions import *
from sumstats.chr.constants import *


def query_for_chromosome(chr_group):
    all_chr_block_groups = utils.get_all_groups_from_parent(chr_group)
    print("block size", len(all_chr_block_groups))
    return myutils.get_query_datasets_from_groups(TO_QUERY_DSETS, all_chr_block_groups)


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

    name_to_dataset = myutils.get_query_datasets_from_groups(TO_QUERY_DSETS, block_groups)

    bp_mask = utils.interval_mask(filter_block_floor, filter_block_ceil, name_to_dataset[BP_DSET])

    if bp_mask is not None:
        name_to_dataset = utils.filter_dictionary_by_mask(name_to_dataset, bp_mask)

    return name_to_dataset


def query_for_snp(chr_group, block_number, snp):
    block_group = utils.get_group_from_parent(chr_group, block_number)
    snp_group = utils.get_group_from_parent(block_group, snp)

    # initialize dictionary of datasets
    name_to_dataset = {dset_name: [] for dset_name in TO_QUERY_DSETS}

    for dset_name in TO_QUERY_DSETS:
        name_to_dataset[dset_name].extend(myutils.get_dset_from_group(dset_name, snp_group, snp))

    return name_to_dataset


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

    chr_group = utils.get_group_from_parent(f, chr)
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

    print("Start filtering")
    print(time.strftime('%a %H:%M:%S'))

    restrictions = []
    if study is not None:
        restrictions.append(EqualityRestriction(study, name_to_dataset[STUDY_DSET]))
    if p_upper_limit is not None or p_lower_limit is not None:
        restrictions.append(IntervalRestriction(p_lower_limit, p_upper_limit, name_to_dataset[MANTISSA_DSET]))

    if restrictions:
        name_to_dataset = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)

    print("Done filtering")
    print(time.strftime('%a %H:%M:%S'))
    print("length", len(name_to_dataset[SNP_DSET]))
    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset][:10])


if __name__ == "__main__":
    main()