"""
    Query 1: Retrieve all information for trait: input = query number (1) and trait name
    Query 2: Retrieve all the information for a study: input = query number (2) and study name and trait name
    Query 3: Retrieve all information (trait, study, pval, chr, or) for a single SNP: input = query number (3) and snp id
    Query 4: Retrieve all information (trait, study, pval, chr, or) for a set of SNPs that belong to a chromosome:
                input = query number (4) and chr (could do this wth other location information)
    Query 5: Retrieve all information for a trait and a single SNP: input = query number (5), trait and snp id
    Query 6: Retrieve all information for a trait and a set of SNPs that belong to a chromosome:
                input = query number (6), trait and chr

    If a p-value threshold is given, all returned values need to be restricted to this threshold
"""

import h5py
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('h5file', help='The name of the HDF5 file')
parser.add_argument('query', help='The nmber of the query to perform')
parser.add_argument('-study', help='The study I am looking for')
parser.add_argument('-trait', help='The trait I am looking for')
parser.add_argument('-snp', help='The SNP I am looking for')
parser.add_argument('-chr', help='The chromosome whose SNPs I want')
parser.add_argument('-under', help='p-value under this threshold')
parser.add_argument('-over', help='p-value under this threshold')

args = parser.parse_args()


def main():
    f = h5py.File(args.h5file, mode="r")
    if args.query == "1":
        if args.trait is None:
            print "Query 1 -- Retrieve all information for a specific trait -- "
            print "input: query number (1) and trait name"
            exit(1)
        else:
            info_array = all_trait_info(f, args.trait)
    elif args.query == "2":
        if args.study is None or args.trait is None:
            print "Query 2 -- Retrieve all the information for a specific study --"
            print "input: query number (2), study name and trait name"
            exit(1)
        else:
            info_array = all_study_info(f, args.trait, args.study)
    elif args.query == "3":
        if args.snp is None:
            print "Query 3 -- Retrieve all information for a single SNP -- "
            print "input: query number (3) and snp id"
            exit(1)
        else:
            info_array = all_snp_info(f, args.snp, None)
    elif args.query == "4":
        if args.chr is None:
            print "Query 4 -- Retrieve all information for SNPs that belong to a chromosome -- "
            print "input: query number (4) and chromosome"
            exit(1)
        else:
            info_array = all_chromosome_info(f, args.chr, None)
    elif args.query == "5":
        if args.trait is None or args.snp is None:
            print "Query 5 -- Retrieve all information for a trait and a single SNP -- "
            print "input: query number (5), trait and snp id"
            exit(1)
        else:
            info_array = all_snp_and_trait_info(f, args.snp, args.trait)
    elif args.query == "6":
        if args.trait is None or args.chr is None:
            print "Query 6 -- Retrieve all information for SNPs that belong to a chromosome and a specific trait -- "
            print "input: query number (6), chromosome and trait"
            exit(1)
        else:
            info_array = all_chromosome_and_trait_info(f, args.chr, args.trait)
    else:
        print "Wrong input"
        exit(1)

    # we assume that they all give back an info_array that contains all the information in a matrix that has gone through column stack
    # and that the second column has the p-values so we can filter based on that
    pval_np = np.asarray(info_array[:,1], dtype=float)
    info_array = filter_all_info(info_array, pval_np, args.under, args.over)
    print_all_info(info_array)


def all_chromosome_and_trait_info(f, chromosome, trait):
    return all_chromosome_info(f, chromosome, trait)


def all_snp_and_trait_info(f, snp, trait):
    return all_snp_info(f, snp, trait)


def all_trait_info(f, trait):
    print "Retrieving info for trait:", trait

    snps, pvals, chr, orvals, belongs_to = retrieve_all_info_for_trait(f, trait)
    return np.column_stack((snps, pvals, chr, orvals, belongs_to))


def all_study_info(f, trait, study):
    print "Retrieving info for study:", study
    study_group = f.get(trait + "/" + study)
    if study_group is not None:
        snps_np = study_group["snps"][:]
        pv_np = study_group["pvals"][:]
        chr_np = study_group["chr"][:]
        or_np = study_group["or"][:]

        return np.column_stack((snps_np, pv_np, chr_np, or_np))
    else:
        print "Not valid trait/study combination"
        exit(1)


def all_snp_info(f, snp, trait):
    print "Retrieving info for snp:", snp
    if trait is None:
        snps, pvals, chr, orvals, belongs_to = retrieve_all_info(f)
    else:
        snps, pvals, chr, orvals, belongs_to = retrieve_all_info_for_trait(f, trait)

    snps_np = np.asarray(snps)
    mask = snps_np == snp

    info_array = np.column_stack((snps, pvals, chr, orvals, belongs_to))
    return info_array[mask]


def all_chromosome_info(f, chromosome, trait):
    print "Retrieving info for chromosome:", chromosome
    if trait is None:
        snps, pvals, chr, orvals, belongs_to = retrieve_all_info(f)
    else:
        snps, pvals, chr, orvals, belongs_to = retrieve_all_info_for_trait(f, trait)

    chr_np = np.asarray(chr)
    mask = chr_np == int(chromosome)

    info_array = np.column_stack((snps, pvals, chr, orvals, belongs_to))
    return info_array[mask]


def retrieve_all_info_for_trait(f, trait):
    trait_group = f.get(trait)
    if trait_group is not None:
        snps = []
        pvals = []
        chr = []
        orvals = []
        belongs_to = np.array([], dtype = None)

        print "looping through trait"
        for x, study_group in trait_group.iteritems():
            snps_temp = study_group["snps"][:]
            snps.extend(snps_temp)
            pvals.extend(study_group["pvals"][:])
            chr.extend(study_group["chr"][:])
            orvals.extend(study_group["or"][:])
            for i in xrange(len(snps_temp)):
                belongs_to = np.append(belongs_to, study_group.name)
        return snps, pvals, chr, orvals, belongs_to
    else:
        print "Trait does not exist", trait
        exit(1)


def retrieve_all_info(f):
    snps = []
    pvals = []
    chr = []
    orvals = []
    belongs_to = np.array([], dtype = None)

    for x, trait_group in f.iteritems():
        for y, study_group in trait_group.iteritems():
            snps_temp = study_group["snps"][:]
            snps.extend(snps_temp)
            pvals.extend(study_group["pvals"][:])
            chr.extend(study_group["chr"][:])
            orvals.extend(study_group["or"][:])
            for i in xrange(len(snps_temp)):
                belongs_to = np.append(belongs_to, study_group.name)

    return snps, pvals, chr, orvals, belongs_to


def threshold(value, action, pvalues_nparray):
    if action == "u":
        mask = pvalues_nparray <= float(value)
        print "values under:", value
    elif action == "o":
        mask = pvalues_nparray >= float(value)
        print "values over:", value

    return mask


def filter_all_info(info_array, pv_np, under, over):
    if under is not None:
        under_mask = threshold(under, "u", pv_np)
        info_array = info_array[under_mask]
        pv_np = pv_np[under_mask]
    if over is not None:
        over_mask = threshold(over, "o", pv_np)
        info_array = info_array[over_mask]
    return info_array


def print_all_info(info_array):
    print info_array.shape
    print "snps \n", info_array[:,0]
    print "pvals \n", info_array[:,1]
    print "chr positions \n", info_array[:,2]
    print "odds ratio values \n", info_array[:,3]
    if info_array.shape[1] > 4:
        print "trait/study \n", info_array[:,4]

if __name__ == "__main__":
    main()
