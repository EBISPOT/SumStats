"""
Utils useful for querying
"""

import numpy as np
import argparse
import utils_q as utils


def get_block_groups_within_range(chr_group, block_size, block_lower, block_upper):
    """
    block_lower and block_upper should be concrete blocks (i.e. factor of the block_size)
    for block size 100, when I say I want block 100-200 I need to get back block groups[100, 200]
     (i.e. all the positions from 0-200)
    """
    if (block_lower % block_size != 0) or (block_upper % block_size != 0):
        print "I can only accept blocks that conform to the block size"
        print "block size: %s, block_lower: %ds(s), block_upper: %ds(s)" % (block_size, block_lower, block_upper)
        raise SystemExit(1)

    blocks = [utils.get_group_from_parent(chr_group, block) for block in
              range(block_lower, (block_upper + block_size), block_size)]
    return blocks


def get_dictionary_of_dsets_from_blocks(block_groups, dsets):
    # initialize dictionary of datasets
    dict_of_dsets = {dset : [] for dset in dsets}

    for block_group in block_groups:
        for snp, snp_group in block_group.iteritems():

            for dset_name in dsets:
                dict_of_dsets[dset_name].extend(get_dset_from_group(dset_name, snp_group, snp))

    for dset in dsets:
        dict_of_dsets[dset] = np.array(dict_of_dsets[dset])

    return dict_of_dsets


def get_dset_from_group(dset_name, group, empty_array_element=None):
    array = utils.get_dset(group, dset_name)
    if (array is None) and (empty_array_element is not None):
        # pval is never empty
        pval = utils.get_dset(group, "pval")
        array = [empty_array_element for _ in xrange(len(pval))]
    return array


def to_list_of_ints(number):
    list = []
    for digit in str(number):
        list.append(int(digit))
    return list


def _fitting_block_size(block_size, bp):
    block = block_size
    while block < bp + block_size and bp >= block:
        block += block_size
    return block


def get_block_number(block_size, bp_position):
    """
    Calculates the block that this BP (base pair location) will belong
    Blocks are saved with their upper limit, i.e. for block size = 100 if
    bp == 50 then it is saved in the block 0-100, so we will get back
    the block name called "100"

    :param block_size: the size of the blocks as they are saved in the chromosome
    :param bp_position: the base pair location
    :return: the upper limit of the block that the bp belongs to
    """
    block_size_as_string = to_list_of_ints(block_size)
    block_size_length = len(block_size_as_string)

    bp_position_as_string = to_list_of_ints(bp_position)
    bp_position_length = len(bp_position_as_string)

    if bp_position == block_size:
        return int(block_size)

    elif bp_position_length < block_size_length:
        return int(block_size)

    elif bp_position_length == block_size_length:
        if bp_position_as_string[0] == block_size_as_string[0]:
            # bp_position is just above the first block size, so we are in the second block
            return int(2 * block_size)
        else:
            # check if all the other bp_position_length match (except the first one), and if so then return bp as the
            #  block
            # if the bp_position_length do not match then give back the next block

            # loop through the rest of the bp_position_length
            is_factor_of = bp_position % block_size == 0
            if is_factor_of:
                return int(bp_position)
            else:
                correct_block = _fitting_block_size(block_size, bp_position)
                return int(correct_block)
    else:
        # bp bp_position_length are bigger than block bp_position_length
        # this means that we should keep the last x bp_position_length of bp
        # where x is the number of bp_position_length in block_size
        # if they are the same then we can again return bp
        # if they are not the same we need to return the last bp_position_length + block_size, and
        # keep the first bp_position_length as they are
        # example block size = 100
        # if bp = 1100 return bp
        # if bp = 1101 return 1200
        last_bp_digits = bp_position_as_string[::-1][0:block_size_length][::-1]
        last_bp_digits_as_int = int("".join(str(x) for x in last_bp_digits))
        is_factor_of = last_bp_digits_as_int % block_size == 0
        if is_factor_of:
            return int(bp_position)
        else:
            first_bp_digits = bp_position_as_string[::-1][block_size_length:][::-1]

            correct_sub_block = _fitting_block_size(block_size, last_bp_digits_as_int)
            # I need to take the first bp bp_position_length, zero out the rest of them
            # and then add the correct sub block

            bp_zeroed_out_array = first_bp_digits
            bp_zeroed_out_array.extend([0 for x in last_bp_digits])

            first_bp_digits = int("".join(str(x) for x in bp_zeroed_out_array))
            correct_block = first_bp_digits + correct_sub_block
            return int(correct_block)


def argument_checker():
    args = argument_parser()

    if args.query == "1":
        # finding block
        if args.bu is None or args.bl is None:
            print "You need to specify an upper and lower limit for the chromosome block (e.g. -bl 0 -bu 100000)"
            raise SystemExit(1)
    elif args.query == "2":
        if args.snp is None:
            print "You need to provide a snp to be looked up (e.g. -snp rs1234)"
            print "If you know it, you can also provide the baise pair location of the snp, or an upper limit close " \
                  "to where you expect it to be (e.g. -bu 123000) "
            raise SystemExit(1)
    else:
        print "Wrong input"
        raise SystemExit(1)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-query', help='1 for finding block, 2 for finding snp', required=True)
    parser.add_argument('-chr', help='The chromosome I am looking for', required=True)
    parser.add_argument('-bu', help='The upper limit of the chromosome block I am looking for (can omit if snp '
                                    'provided)')
    parser.add_argument('-bl', help='The lower limit of the chromosome block I am looking for (can omit if snp '
                                    'provided)')
    parser.add_argument('-snp', help='The SNP I am looking for (can omit if chr and block provided)')
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