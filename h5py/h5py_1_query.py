"""
    Data is stored in the hierarchy of Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    snparray will hold the snp ids
    pvals will hold each snps pvalue for this study
    chr will hold each snps position
    or_array will hold each snps odds ratio for this study
    we can add any other information that we want

    the positions in the vectors correspond to each other
    snparray[0], pvals[0], chr[0], and or_array[0] hold the information for SNP 0

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
import pandas as pd
import codecs, json

def main():

    qu.argument_checker()
    args = qu.argument_parser()

    # open h5 file in read mode
    f = h5py.File(args.h5file, mode="r")

    if args.query == "1":
        # info_array = all_trait_info(f, args.trait)
        snps, pvals, chr, orvals, belong_to = all_trait_info(f, args.trait)
    elif args.query == "2":
        snps, pvals, chr, orvals, belong_to = all_study_info(f, args.trait, args.study)
    elif args.query == "3":
        snps, pvals, chr, orvals, belong_to = all_snp_info(f, args.snp)
    elif args.query == "4":
        snps, pvals, chr, orvals, belong_to = all_chromosome_info(f, args.chr)
    elif args.query == "5":
        snps, pvals, chr, orvals, belong_to = all_snp_info(f, args.snp, args.trait)
    elif args.query == "6":
        snps, pvals, chr, orvals, belong_to = all_chromosome_info(f, args.chr, args.trait)

    mask = qu.pval_mask(pvals, args.under, args.over)
    if mask is not None:
        print qu.filter_vector(snps, mask)
        print qu.filter_vector(pvals, mask)
        print qu.filter_vector(chr, mask)
        print qu.filter_vector(orvals, mask)
        print qu.filter_vector(np.asarray(belong_to, dtype = None), mask)
    else:
        print snps
        print pvals
        print chr
        print orvals
        print belong_to

    # pval_np = np.asarray(info_array[:,1], dtype=float)
    # info_array = qu.filter_all_info(info_array, pval_np, args.under, args.over)
    # b = info_array.tolist()
    # file_path = "./path.json"
    # json.dump(b, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)

    # qu.print_all_info(info_array)


def all_trait_info(f, trait):
    print "Retrieving info for trait:", trait
    trait_group = f.get(trait)
    snps = None
    pvals = None
    chr = None
    orvals = None
    belongs_to = None
    if trait_group is not None:
        print "looping through trait"
        for study_group_name, study_group in trait_group.iteritems():
            snps_r, pvals_r, chr_r, orvals_r, belongs_to_r = retrieve_all_info_from_study(study_group_name, study_group)
            if snps is None:
                snps = snps_r
                pvals = pvals_r
                chr = chr_r
                orvals = orvals_r
                belongs_to = belongs_to_r
            else:
                snps = np.concatenate((snps, snps_r))
                pvals = np.concatenate((pvals, pvals_r))
                chr = np.concatenate((chr, chr_r))
                orvals = np.concatenate((orvals, orvals_r))
                belongs_to = np.concatenate((belongs_to, belongs_to_r))
        return snps, pvals, chr, orvals, belongs_to
    else:
        print "Trait does not exist", trait
        exit(1)


def all_study_info(f, trait, study):
    print "Retrieving info for study:", study
    study_group = f.get(trait + "/" + study)
    if study_group is not None:
        return retrieve_all_info_from_study(study, study_group)
    else:
        print "Not valid trait/study combination"
        exit(1)


def all_snp_info(f, snp, trait=None):
    print "Retrieving info for snp:", snp
    if trait is None:
        snps, pvals, chr, orvals, belongs_to = retrieve_all_info(f)
    else:
        snps, pvals, chr, orvals, belongs_to = all_trait_info(f, trait)

    mask = snps == snp

    return qu.filter_vector(snps, mask), qu.filter_vector(pvals, mask), qu.filter_vector(chr, mask), qu.filter_vector(orvals, mask), qu.filter_vector(np.asarray(belongs_to, dtype=None), mask)


def all_chromosome_info(f, chromosome, trait=None):
    print "Retrieving info for chromosome:", chromosome
    if trait is None:
        snps, pvals, chr, orvals, belongs_to = retrieve_all_info(f)
    else:
        snps, pvals, chr, orvals, belongs_to = all_trait_info(f, trait)

    mask = chr == float(chromosome)

    return qu.filter_vector(snps, mask), qu.filter_vector(pvals, mask), qu.filter_vector(chr, mask), qu.filter_vector(orvals, mask), qu.filter_vector(np.asarray(belongs_to, dtype = None), mask)


def retrieve_all_info(f):
    snps = None
    pvals = None
    chr = None
    orvals = None
    belongs_to = None
    for x, trait_group in f.iteritems():
        for study_group_name, study_group in trait_group.iteritems():
            snps_r, pvals_r, chr_r, orvals_r, belongs_to_r = retrieve_all_info_from_study(study_group_name, study_group)
            if snps is None:
                snps = snps_r
                pvals = pvals_r
                chr = chr_r
                orvals = orvals_r
                belongs_to = belongs_to_r
            else:
                snps = np.concatenate((snps, snps_r))
                pvals = np.concatenate((pvals, pvals_r))
                chr = np.concatenate((chr, chr_r))
                orvals = np.concatenate((orvals, orvals_r))
                belongs_to = np.concatenate((belongs_to, belongs_to_r))

    return snps, pvals, chr, orvals, belongs_to


def retrieve_all_info_from_study(study_group_name, study_group):
    snps = study_group["snps"][:]
    pvals = study_group["pvals"][:]
    chr = study_group["chr"][:]
    orvals = study_group["or"][:]
    belongs_to = [study_group_name for i in xrange(len(snps))]
    return snps, pvals, chr, orvals, belongs_to



if __name__ == "__main__":
    main()
