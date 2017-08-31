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
import numpy as np
import query_utils as qu


def main():

    qu.argument_checker()
    args = qu.argument_parser()

    # open h5 file in read mode
    f = h5py.File(args.h5file, mode="r")

    if args.query == "1":
        info_array = all_trait_info(f, args.trait)
    elif args.query == "2":
        info_array = all_study_info(f, args.trait, args.study)
    elif args.query == "3":
        info_array = all_snp_info(f, args.snp, None)
    elif args.query == "4":
        info_array = all_chromosome_info(f, args.chr, None)
    elif args.query == "5":
        info_array = all_snp_info(f, args.snp, args.trait)
    elif args.query == "6":
        info_array = all_chromosome_info(f, args.chr, args.trait)

    # we assume that they all give back an info_array that contains all the information in a matrix that has gone
    # through column stack and that the second column has the p-values so we can filter based on that

    pval_np = np.asarray(info_array[:,1], dtype=float)
    info_array = qu.filter_all_info(info_array, pval_np, args.under, args.over)
    qu.print_all_info(info_array)


def all_trait_info(f, trait):
    print "Retrieving info for trait:", trait
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
        return np.column_stack((snps, pvals, chr, orvals, belongs_to))
    else:
        print "Trait does not exist", trait
        exit(1)


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
        info_array = retrieve_all_info(f)
    else:
        info_array = all_trait_info(f, trait)

    snps_np = np.asarray(info_array[:,1], dtype=None)
    mask = snps_np == snp

    return info_array[mask]


def all_chromosome_info(f, chromosome, trait):
    print "Retrieving info for chromosome:", chromosome
    if trait is None:
        info_array = retrieve_all_info(f)
    else:
        info_array = all_trait_info(f, trait)

    chr_np = np.asarray(info_array[:,2], dtype=float)
    mask = chr_np == float(chromosome)

    return info_array[mask]


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

    return np.column_stack((snps, pvals, chr, orvals, belongs_to))


if __name__ == "__main__":
    main()
