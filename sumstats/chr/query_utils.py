"""
Utils useful for querying
"""

import argparse
from sumstats.chr.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group_utils as gu


def get_block_groups_from_parent_within_block_range(chr_group, block_lower, block_upper):
    """
    block_lower and block_upper should be concrete blocks (i.e. factor of the block_size)
    for block size 100, when I say I want block 100-200 I need to get back block groups[100, 200]
     (i.e. all the positions from 0-200)
    """
    if (block_lower % BLOCK_SIZE != 0) or (block_upper % BLOCK_SIZE != 0):
        raise ValueError("block sizes not conforming to the block size: %s, block_lower: %ds(s), block_upper: %ds(s)" % (BLOCK_SIZE, block_lower, block_upper))
    if block_lower > block_upper:
        raise ValueError("lower limit is bigger than upper limit")

    blocks = [gu.get_group_from_parent(chr_group, block) for block in
              range(block_lower, (block_upper + BLOCK_SIZE), BLOCK_SIZE)]
    return blocks


def get_query_datasets_from_groups(groups):
    # initialize dictionary of datasets
    name_to_dataset = {dset : Dataset([]) for dset in TO_QUERY_DSETS}

    for block_group in groups:
        for snp, snp_group in block_group.items():
            name_to_dataset = extend_datasets_for_group(snp, snp_group, name_to_dataset)
    return name_to_dataset


def extend_datasets_for_group(snp, snp_group, name_to_dataset):
    for name, dataset in name_to_dataset.items():
        if name != SNP_DSET:
            dataset.extend(gu.get_dset_from_group(name, snp_group))

    temp_dset = gu.get_dset_from_group(BP_DSET, snp_group)
    name_to_dataset[SNP_DSET].extend(gu.create_dset_placeholder(len(temp_dset), snp))
    return name_to_dataset


def get_block_number(bp_position):
    """
    Calculates the block that this BP (base pair location) will belong
    Blocks are saved with their upper limit, i.e. for block size = 100 if
    bp == 50 then it is saved in the block 0-100, so we will get back
    the block name called "100"

    :param bp_position: the base pair location
    :return: the upper limit of the block that the bp belongs to
    """

    if bp_position <= BLOCK_SIZE:
        return BLOCK_SIZE
    else:
        is_factor_of_block_size = bp_position % BLOCK_SIZE == 0
        if is_factor_of_block_size:
            return bp_position
        else:
            return bp_position - (bp_position % BLOCK_SIZE) + BLOCK_SIZE


def argument_checker():
    args = argument_parser()

    if args.query == "1":
        pass
    elif args.query == "2":
        if args.snp is None:
            raise ValueError("You need to provide a snp to be looked up (e.g. -snp rs1234)")
    else:
        raise ValueError("Wrong input")


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-query', help='1 for finding block, 2 for finding snp', required=True)
    parser.add_argument('-chr', help='The chromosome I am looking for', required=True)
    parser.add_argument('-bu', help='The upper limit of the chromosome block I am looking for (can omit if snp '
                                    'provided)')
    parser.add_argument('-bl', help='The lower limit of the chromosome block I am looking for (can omit if snp '
                                    'provided)')
    parser.add_argument('-snp', help='The SNP I am looking for. Please provide -bu if known. (Can omit if chr and '
                                     'block provided).')
    parser.add_argument('-study', help='Filter results for a specific study')
    parser.add_argument('-pu', help='The upper limit for the p-value')
    parser.add_argument('-pl', help='The lower limit for the p-value')
    return parser.parse_args()


def convert_args(args):
    chr = int(args.chr)
    query = int(args.query)
    block_upper_limit = args.bu
    if block_upper_limit is not None:
        block_upper_limit = int(block_upper_limit)
    block_lower_limit = args.bl
    if block_lower_limit is not None:
        block_lower_limit = int(block_lower_limit)

    snp = args.snp

    study = args.study
    p_upper_limit = args.pu
    if p_upper_limit is not None:
        p_upper_limit = float(p_upper_limit)
    p_lower_limit = args.pl
    if p_lower_limit is not None:
        p_lower_limit = float(p_lower_limit)

    return chr, query, block_upper_limit, block_lower_limit, snp, study, p_upper_limit, p_lower_limit