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


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help = 'The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-chr', help = 'The chromosome I am looking for', required=True)
    parser.add_argument('-snp', help = 'The SNP I am looking for (can omit if chr provided)')
    parser.add_argument('-study', help='The study I am looking for')
    parser.add_argument('-under', help='p-value under this threshold')
    parser.add_argument('-over', help='p-value under this threshold')
    args = parser.parse_args()

    chr = args.chr
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
        for name, snp_group in chr_group.iteritems():
            pvals_tmp = snp_group.get("pvals")[:]
            pvals.extend(pvals_tmp)
            orvals.extend(snp_group.get("or")[:])
            studies.extend(snp_group.get("studies")[:])
            snps.extend(([name for i in range(0, len(pvals_tmp))]))
            if len(snps) % 100000 == 0:
                print "Loaded %s so far..." % (len(snps))

        print "Filtering study starts..."
        pvals, orvals, studies, snps = filter_by_study(study, np.asarray(pvals), np.asarray(orvals), np.asarray(studies), snps=np.asarray(snps))
        print "Filtering study done..."
        print "Filtering under starts..."
        pvals, orvals, studies, snps = filter_by_pval_under(under, pvals, orvals, studies, snps=snps)
        print "Filtering under done..."
        print "Filtering over starts..."
        pvals, orvals, studies, snps = filter_by_pval_over(over, pvals, orvals, studies, snps=snps)
        print "Filtering over done..."

        print "snps"
        print snps
        print "pvals"
        print pvals
        print "orvals"
        print orvals
        print "studies"
        print studies

    else:
        snp_group = get_snp_group(chr_group, snp)
        pvals = snp_group.get("pvals")[:]
        orvals = snp_group.get("or")[:]
        studies = snp_group.get("studies")[:]

        pvals, orvals, studies = filter_by_study(study, pvals, orvals, studies)
        pvals, orvals, studies = filter_by_pval_under(under, pvals, orvals, studies)
        pvals, orvals, studies = filter_by_pval_over(over, pvals, orvals, studies)

        print "pvals"
        print pvals
        print "orvals"
        print orvals
        print "studies"
        print studies


def get_snp_group(chr_group, snp):
    snp_group = chr_group.get(snp)
    if snp_group is None:
        print "snp %s does not exist for chromosome %s" % (snp, chr_group.name)
        raise SystemExit(1)
    return snp_group


def get_chromosome_group(f, chr):
    chr_group = f.get(chr)
    if chr_group is None:
        print "Chromosome does not exist in file!"
        raise SystemExit(1)
    return chr_group


# filter the study if it is specified
def filter_by_study(study, pvals, orvals, studies, snps=None):
    if study is not None:
        mask = studies == study
        pvals = pvals[mask]
        orvals = orvals[mask]
        studies = studies[mask]
        if snps is not None:
            snps = snps[mask]
            return pvals, orvals, studies, snps
    if snps is None:
        return pvals, orvals, studies
    else:
        return pvals, orvals, studies, snps


def filter_by_pval_under(under, pvals, orvals, studies, snps=None):
    if under is not None:
        mask = pvals <= float(under)
        pvals = pvals[mask]
        orvals = orvals[mask]
        studies = studies[mask]
        if snps is not None:
            snps = snps[mask]
            return pvals, orvals, studies, snps
    if snps is None:
        return pvals, orvals, studies
    else:
        return pvals, orvals, studies, snps


def filter_by_pval_over(over, pvals, orvals, studies, snps=None):
    if over is not None:
        mask = pvals >= float(over)
        pvals = pvals[mask]
        orvals = orvals[mask]
        studies = studies[mask]
        if snps is not None:
            snps = snps[mask]
            return pvals, orvals, studies, snps
    if snps is None:
        return pvals, orvals, studies
    else:
        return pvals, orvals, studies, snps


if __name__ == "__main__":
    main()


