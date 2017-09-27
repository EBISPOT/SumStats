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


def get_snp_group(block_group, snp):
    snp_group = block_group.get(snp)
    if snp_group is None:
        print "snp %s does not exist for this block %s" % (snp, block_group.name)
        raise SystemExit(1)
    return snp_group


def get_block_group(chr_group, block):
    block_group = chr_group.get(chr)
    if block_group is None:
        print "Block does not exist in this chromosome!"
        raise SystemExit(1)
    return block_group


def get_chromosome_group(f, chr):
    chr_group = f.get(chr)
    if chr_group is None:
        print "Chromosome does not exist in file!"
        raise SystemExit(1)
    return chr_group


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


def filter_by_mask(vector, mask):
    return vector[mask]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-chr', help='The chromosome I am looking for', required=True)
    parser.add_argument('-block', help='The chromosome block I am looking for', required=True)
    parser.add_argument('-snp', help='The SNP I am looking for (can omit if chr provided)')
    parser.add_argument('-study', help='The study I am looking for')
    parser.add_argument('-under', help='p-value under this threshold')
    parser.add_argument('-over', help='p-value under this threshold')
    args = parser.parse_args()

    chr = args.chr
    block = args.block
    snp = args.snp
    study = args.study
    under = args.under
    over = args.over

    # open h5 file in read mode
    f = h5py.File(args.h5file, mode="r")

    # get all info for the whole chromosome!
    chr_group = get_chromosome_group(f, chr)

    if snp is None:
        snps = []
        pvals = []
        orvals = []
        studies = []
        bp = []
        effect = []
        other = []
        for name, block_group in chr_group.iteritems():
            for name, snp_group in block_group.iteritems():
                pvals_tmp = snp_group.get("pval")[:]
                pvals.extend(pvals_tmp)
                orvals.extend(snp_group.get("or")[:])
                studies.extend(snp_group.get("study")[:])
                bp.extend(snp_group.get("bp")[:])
                effect.extend(snp_group.get("effect")[:])
                other.extend(snp_group.get("other")[:])
                # snp id is in the name of the group, not a dataset
                snps.extend(([name for i in range(0, len(pvals_tmp))]))
                if len(snps) % 100000 == 0:
                    print "Loaded %s so far..." % (len(snps))

    else:
        block_group = get_block_group(chr_group, block)
        snp_group = get_snp_group(block_group, snp)

        snps = None
        orvals = snp_group.get("or")[:]
        studies = snp_group.get("study")[:]
        bp = snp_group.get("bp")[:]
        effect = snp_group.get("effect")[:]
        other = snp_group.get("other")[:]

    print "Filtering study starts..."
    study_mask = get_study_mask(study, studies)
    if study_mask is not None:
        if snps is not None:
            snps = filter_by_mask(snps, study_mask)
        pvals = filter_by_mask(pvals, study_mask)
        orvals = filter_by_mask(orvals, study_mask)
        studies = filter_by_mask(studies, study_mask)
        bp = filter_by_mask(bp, study_mask)
        effect = filter_by_mask(effect, study_mask)
        other = filter_by_mask(other, study_mask)
    print "Filtering study done..."

    print "Filtering under starts..."
    pval_under_mask = get_pval_under_mask(under, pvals)
    if pval_under_mask is not None:
        if snps is not None:
            snps = filter_by_mask(snps, pval_under_mask)
        pvals = filter_by_mask(pvals, pval_under_mask)
        orvals = filter_by_mask(orvals, pval_under_mask)
        studies = filter_by_mask(studies, pval_under_mask)
        bp = filter_by_mask(bp, pval_under_mask)
        effect = filter_by_mask(effect, pval_under_mask)
        other = filter_by_mask(other, pval_under_mask)
    print "Filtering under done..."

    print "Filtering over starts..."
    pval_over_mask = get_pval_over_mask(over, pvals)
    if pval_over_mask is not None:
        if snps is not None:
            snps = filter_by_mask(snps, pval_over_mask)
        pvals = filter_by_mask(pvals, pval_over_mask)
        orvals = filter_by_mask(orvals, pval_over_mask)
        studies = filter_by_mask(studies, pval_over_mask)
        bp = filter_by_mask(bp, pval_over_mask)
        effect = filter_by_mask(effect, pval_over_mask)
        other = filter_by_mask(other, pval_over_mask)
    print "Filtering over done..."

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
