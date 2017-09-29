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
import argparse
from utils_q import *


def query_for_block(chr_group, block_size, block_lower, block_upper):
    bp_under = None
    bp_over = None
    # for block size 100, if I say I want BP range 250 - 350 that means
    # I need to search from block 200-300 and 300-400
    # get_block for 250 will give me the upper limit of this block, so 300
    # therefore I am reducing the block lower limit by block size, i.e. 200.
    # for 350 I will get back 400, so now I am searching from 200 to 400
    fitted_block_lower = get_block(block_size, block_lower) - block_size
    fitted_block_upper = get_block(block_size, block_upper)

    block_groups = get_block_groups(chr_group, fitted_block_lower, fitted_block_upper, block_size)

    # we might need to filter further if they don't fit exactly
    # e.g. we got the snps for range 200-400 now we need to filter 250-350
    if fitted_block_lower != block_lower:
        bp_over = block_lower
    if fitted_block_upper != block_upper:
        bp_under = block_upper

    snps = []
    pvals = []
    orvals = []
    studies = []
    bp = []
    effect = []
    other = []

    for block_group in block_groups:
        for name, snp_group in block_group.iteritems():
            snps_r, pvals_r, orvals_r, studies_r, bp_r, effect_r, other_r = get_snp_group_info(snp_group, name)
            snps.extend(snps_r)
            pvals.extend(pvals_r)
            orvals.extend(orvals_r)
            studies.extend(studies_r)
            bp.extend(bp_r)
            effect.extend(effect_r)
            other.extend(other_r)

    snps = np.array(snps)
    pvals = np.array(pvals)
    orvals = np.array(orvals)
    studies = np.array(studies)
    bp = np.array(bp)
    effect = np.array(effect)
    other = np.array(other)

    bp_mask = cutoff_mask(bp, bp_under, bp_over)
    if bp_mask is not None:
        print "Filtering BP starts..."
        if snps is not None:
            snps = filter_by_mask(snps, bp_mask)
        pvals = filter_by_mask(pvals, bp_mask)
        orvals = filter_by_mask(orvals, bp_mask)
        studies = filter_by_mask(studies, bp_mask)
        bp = filter_by_mask(bp, bp_mask)
        effect = filter_by_mask(effect, bp_mask)
        other = filter_by_mask(other, bp_mask)
        print "Filtering BP done..."

    return snps, pvals, orvals, studies, bp, effect, other


def query_for_snp(chr_group, block, snp):
    block_group = get_block_group(chr_group, block)
    snp_group = get_snp_group(block_group, snp)
    return get_snp_group_info(snp_group, None)


def findspecial(name, obj):
    if snp in name:
        return obj.name


def find_snp_block(chr_group):
    group_name = chr_group.visititems(findspecial)
    name_array = group_name.split("/")
    return name_array[2]


def main():
    global snp
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
    args = parser.parse_args()

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

    # open h5 file in read mode
    f = h5py.File(args.h5file, mode="r")

    # get all info for the whole chromosome!
    chr_group = get_chromosome_group(f, chr)
    block_size = 100000

    if block_upper_limit is None:
        snp_block = find_snp_block(chr_group)
        print snp_block
    else:
        snp_block = get_block(block_size, block_upper_limit)

    if query == 1:
        # finding block
        if block_upper_limit is None or block_lower_limit is None:
            print "You need to specify an upper and lower limit for the chromosome block (e.g. -bl 0 -bu 100000)"
            raise SystemExit(1)
        snps, pvals, orvals, studies, bp, effect, other = query_for_block(chr_group, block_size, block_lower_limit,
                                                                          block_upper_limit)

    else:  # query == 2
        if snp is None:
            print "You need to provide a snp to be looked up (e.g. -snp rs1234)"
            print "If you know it, you can also provide the baise pair location of the snp, or an upper limit close " \
                  "to where you expect it to be (e.g. -bu 123000) "
            raise SystemExit(1)
        snps, pvals, orvals, studies, bp, effect, other = query_for_snp(chr_group, snp_block, snp)

    # start filtering based on study and pval thresholds
    study_mask = get_equality_mask(study, studies)
    if study_mask is not None:
        print "Filtering study starts..."
        if snps is not None:
            snps = filter_by_mask(snps, study_mask)
        pvals = filter_by_mask(pvals, study_mask)
        orvals = filter_by_mask(orvals, study_mask)
        studies = filter_by_mask(studies, study_mask)
        bp = filter_by_mask(bp, study_mask)
        effect = filter_by_mask(effect, study_mask)
        other = filter_by_mask(other, study_mask)
        print "Filtering study done..."

    pval_mask = cutoff_mask(pvals, p_upper_limit, p_lower_limit)
    if pval_mask is not None:
        print "Filtering starts..."
        if snps is not None:
            snps = filter_by_mask(snps, pval_mask)
        pvals = filter_by_mask(pvals, pval_mask)
        orvals = filter_by_mask(orvals, pval_mask)
        studies = filter_by_mask(studies, pval_mask)
        bp = filter_by_mask(bp, pval_mask)
        effect = filter_by_mask(effect, pval_mask)
        other = filter_by_mask(other, pval_mask)
        print "Filtering pval done..."


    print "snps"
    print snps
    print "pvals"
    print pvals
    print "orvals"
    print orvals
    print "studies"
    print studies
    print "BP"
    print bp
    print "Effect Allele"
    print effect
    print "Other Allele"
    print other


if __name__ == "__main__":
    main()
