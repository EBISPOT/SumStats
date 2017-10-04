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

import h5py
import numpy as np

import query_utils as myutils
from sumstats import utils


def query_for_block_range(chr_group, block_size, block_lower_limit, block_upper_limit):
    filter_block_under = None
    filter_block_over = None
    # for block size 100, if I say I want BP range 250 - 350 that means
    # I need to search for block 300 (200-300) and block 400 (300-400)

    from_block = myutils.get_block_number(block_size, block_lower_limit)
    to_block = myutils.get_block_number(block_size, block_upper_limit)

    block_groups = myutils.get_block_groups_within_range(chr_group, block_size, from_block, to_block)

    # we might need to filter further if they don't fit exactly
    # e.g. we got the snps for range 200-400 now we need to filter 250-350
    if from_block != block_lower_limit:
        filter_block_over = block_lower_limit
    if to_block != block_upper_limit:
        filter_block_under = block_upper_limit

    dictionary_of_dsets = myutils.get_dictionary_of_dsets_from_blocks(block_groups, names_of_dsets)

    bp_mask = utils.cutoff_mask(dictionary_of_dsets["bp"], filter_block_under, filter_block_over)

    if bp_mask is not None:
        dictionary_of_dsets = utils.filter_dictionary_by_mask(dictionary_of_dsets, bp_mask)

    return dictionary_of_dsets


def query_for_snp(chr_group, block, snp):
    block_group = utils.get_group_from_parent(chr_group, block)
    snp_group = utils.get_group_from_parent(block_group, snp)

    # initialize dictionary of datasets
    dictionary_of_dsets = {dset_name : [] for dset_name in names_of_dsets}

    for dset_name in names_of_dsets:
        dictionary_of_dsets[dset_name].extend(myutils.get_dset_from_group(dset_name, snp_group, snp))

    for dset_name in names_of_dsets:
        dictionary_of_dsets[dset_name] = np.array(dictionary_of_dsets[dset_name])

    return dictionary_of_dsets


def find_snp_in_group_name(name, group):
    if snp in name:
        return group.name


def find_snp_block(chr_group, snp):

    # def find_snp_in_group_name(name, group):
    #     if snp in name:
    #         return group.name

    group_name = chr_group.visititems(find_snp_in_group_name)
    name_array = group_name.split("/")
    return name_array[2]


def get_block_that_snp_belongs_to(chr_group, block_size, block_upper_limit, snp):
    if block_upper_limit is None:
        snp_block = find_snp_block(chr_group, snp)
    else:
        snp_block = myutils.get_block_number(block_size, block_upper_limit)
    return snp_block


names_of_dsets = ["snp", "pval", "or", "study", "bp", "effect", "other"]


def main():
    global snp
    myutils.argument_checker()
    args = myutils.argument_parser()

    # read the arguments correctly
    chr, query, block_upper_limit, block_lower_limit, snp, study, p_upper_limit, p_lower_limit = myutils.convert_args(args)

    # open h5 file in read mode
    f = h5py.File(args.h5file, mode="r")

    chr_group = utils.get_group_from_parent(f, chr)
    block_size = 100000

    if query == 1:
        dictionary_of_dsets = query_for_block_range(chr_group, block_size, block_lower_limit,
                                                    block_upper_limit)
    elif query == 2:
        snp_block = get_block_that_snp_belongs_to(chr_group, block_size, block_upper_limit, snp)
        dictionary_of_dsets = query_for_snp(chr_group, snp_block, snp)

    study_mask = utils.get_equality_mask(study, dictionary_of_dsets["study"])
    pval_mask = utils.cutoff_mask(dictionary_of_dsets["pval"], p_upper_limit, p_lower_limit)

    filtering_mask = utils.combine_masks(study_mask, pval_mask)

    if filtering_mask is not None:
        dictionary_of_dsets = utils.filter_dictionary_by_mask(dictionary_of_dsets, filtering_mask)

    for dset in dictionary_of_dsets:
        print(dset)
        print(dictionary_of_dsets[dset])


if __name__ == "__main__":
    main()