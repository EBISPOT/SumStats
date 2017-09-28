"""
Utils useful for querying
"""

import h5py
import numpy as np


def get_snp_group(block_group, snp):
    snp_group = block_group.get(str(snp))
    if snp_group is None:
        print "snp %s does not exist for this block %s" % (snp, block_group.name)
        raise SystemExit(1)
    return snp_group


def get_block_groups(chr_group, block_lower, block_upper, block_size):
    # for block size 100, when I say I want block 0-100 I need to get back block 100 (i.e. all the positions from 0-100)
    # so range block_lower + block_size = 0 + 100 = 100 to block_upper + block_size = 100 + 100 = 200
    # range 100,200,100 will only search for block 100, which holds the positions 0-100
    blocks = [get_block_group(chr_group, block) for block in range((block_lower + block_size), (block_upper + block_size), block_size)]
    return blocks


def get_block_group(chr_group, block):
    block_group = chr_group.get(str(block))
    if block_group is None:
        print "Block does not exist in this chromosome", block
        raise SystemExit(1)
    return block_group


def get_chromosome_group(f, chr):
    chr_group = f.get(str(chr))
    if chr_group is None:
        print "Chromosome does not exist in file!"
        raise SystemExit(1)
    return chr_group


def get_snp_group_info(snp_group, snp=None):
    pvals_tmp = snp_group.get("pval")[:]
    pvals = pvals_tmp
    orvals = snp_group.get("or")[:]
    studies = snp_group.get("study")[:]
    bp = snp_group.get("bp")[:]
    effect = snp_group.get("effect")[:]
    other = snp_group.get("other")[:]
    if snp is not None:
        # snp id is in the name of the group, not a dataset
        snps = ([snp for i in range(0, len(pvals_tmp))])
    else:
        snps = None
    return snps, pvals, orvals, studies, bp, effect, other


# filter the study if it is specified
def get_study_mask(study, studies):
    mask = None
    if study is not None:
        mask = studies == study

    return mask


def get_pval_under_mask(under, pvals):
    mask = None
    if under is not None:
        mask = pvals <= float(under)
    return mask


def get_pval_over_mask(over, pvals):
    mask = None
    if over is not None:
        mask = pvals >= float(over)
    return mask


def get_bp_under_mask(under, bps):
    mask = None
    if under is not None:
        mask = bps <= int(under)

    return mask


def get_bp_over_mask(over, bps):
    mask = None
    if over is not None:
        mask = bps >= int(over)
    return mask


def filter_by_mask(vector, mask):
    return vector[mask]


def same_digits(list1, list2):
    same = True
    for i in range(1, len(list2)):
        if list1[i] != list2[i]:
            same = False
            break
    return same


def fitting_block_size(block_size, bp):
    i = block_size
    while i < bp + block_size and bp >= i:
        i += block_size
    return i


def to_list_of_ints(number):
    list = []
    for digit in str(number):
        list.append(int(digit))
    return list


def get_block(block_size, bp):
    str_block = to_list_of_ints(block_size)
    block_digits = len(str_block)

    str_bp = to_list_of_ints(bp)
    digits = len(str_bp)

    if bp == block_size:
        return block_size

    elif digits < block_digits:
        return int(block_size)

    elif digits == block_digits:
        if str_bp[0] == str_block[0]:
            # we are here, it is not == block size because if it was then we would have caught that already
            # we are just above the first block size, so we are in the second block
            return int(2 * block_size)
        else:
            # check if all the other digits match (except the first one), and if so then return bp as the block
            # if the digits do not match then give back the next block

            # loop through the rest of the digits

            same = same_digits(str_bp, str_block)
            if same:
                return int(bp)
            else:
                correct_block = fitting_block_size(block_size, bp)
                return int(correct_block)
    else:
        # bp digits are bigger than block digits
        # this means that we should keep the last x digits of bp
        # where x is the number of digits in block_size
        # if they are the same then we can again return bp
        # if they are not the same we need to return the last digits + block_size, and
        # keep the first digits as they are
        # example block size = 100
        # if bp = 1100 return bp
        # if bp = 1101 return 1200
        last_bp_digits = str_bp[::-1][0:block_digits][::-1]
        same = same_digits(last_bp_digits, str_block)
        if same:
            return int(bp)
        else:
            first_bp_digits = str_bp[::-1][block_digits:][::-1]
            last_bp_digits_as_int = int("".join(str(x) for x in last_bp_digits))

            correct_sub_block = fitting_block_size(block_size, last_bp_digits_as_int)
            # I need to take the first bp digits, zero out the rest of them
            # and then add the correct sub block

            bp_zeroed_out_array = first_bp_digits
            bp_zeroed_out_array.extend([0 for x in last_bp_digits])

            first_bp_digits = int("".join(str(x) for x in bp_zeroed_out_array))
            correct_block = first_bp_digits + correct_sub_block
            return int(correct_block)