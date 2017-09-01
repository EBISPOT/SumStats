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
        trait_group = f.get(args.trait)
        if trait_group is not None:
            info_array = retrieve_all_info_for_trait(trait_group)
        else:
            print "Trait does not exist!", args.trait
            exit(1)
    elif args.query == "2":
        info_array = all_study_info(f, args.trait, args.study)
    elif args.query == "3":
        if args.chr is None:
            print "You need to specify the chromosome the SNP belongs to"
            exit(1)
        info_array = all_snp_info(f, args.chr, args.snp)
    elif args.query == "4":
        info_array = all_chromosome_info(f, args.chr)
    elif args.query == "5":
        if args.chr is None:
            print "You need to specify the chromosome the SNP belongs to"
            exit(1)
        info_array = all_snp_info(f, args.chr, args.snp, args.trait)
    elif args.query == "6":
        info_array = all_chromosome_info(f, args.chr, args.trait)

    # we assume that they all give back an info_array that contains all the information in a matrix that has gone
    # through column stack and that the second column has the p-values so we can filter based on that

    pval_np = np.asarray(info_array[:,1], dtype=float)
    info_array = qu.filter_all_info(info_array, pval_np, args.under, args.over)
    qu.print_all_info(info_array)


def retrieve_all_info_for_trait(trait_group):
    info_array = None
    for x, chr in trait_group.iteritems():
        for y, snp_group in chr.iteritems():
            if info_array is None:
                info_array = gather_info_from_snp_group(snp_group)
            else:
                info_array = np.row_stack((info_array, gather_info_from_snp_group(snp_group)))

    return info_array


def all_study_info(f, trait, study):
    trait_group = f.get(trait)
    if trait_group is None:
        print "Trait does not exist!"
        exit(1)

    info_trait_array = retrieve_all_info_for_trait(trait_group)
    return info_trait_array[info_trait_array[:,4] == study]


def all_snp_info(f, chr, snp):
    info_array = None
    # loop though all traits to find the study
    for x, trait_group in f.iteritems():
        snp_group = trait_group.get(chr + "/" + snp)

        if snp_group is None:
            print "Chromosome/SNP combination does not exist"
            exit(1)

        if info_array is None:
            info_array = gather_info_from_snp_group(snp_group)
        else:
            info_array = np.row_stack((info_array, gather_info_from_snp_group(snp_group)))

    return info_array


def all_snp_info(f, chr, snp, trait):
    snp_group = f.get(trait + "/" + chr + "/" + snp)
    if snp_group is None:
        print "Wrong combination of trait/chr/snp"
        exit(1)
    return gather_info_from_snp_group(snp_group)


def all_chromosome_info(f, chr):
    info_array = None
    # loop through all the traits to find the collect the chromosome data
    for x, trait_group in f.iteritems():
        chr_group = trait_group.get(chr)
        # for each chromosome get all the snp information
        for y, snp_group in chr_group.iteritems():
            if info_array is None:
                info_array = gather_info_from_snp_group(snp_group)
            else:
                info_array = np.row_stack((info_array, gather_info_from_snp_group(snp_group)))

    return info_array


def all_chromosome_info(f, chr, trait):
    info_array = None
    trait_group = f.get(trait)
    if trait_group is None:
        print "Trait does not exist!"
        exit(1)

    chr_group = trait_group.get(chr)
    # for each chromosome get all the snp information
    for y, snp_group in chr_group.iteritems():
        if info_array is None:
            info_array = gather_info_from_snp_group(snp_group)
        else:
            info_array = np.row_stack((info_array, gather_info_from_snp_group(snp_group)))

    return info_array


def gather_info_from_snp_group(snp_group):
    info_array = None
    studies_dset = snp_group['studies']
    snps = [snp_group.name.split("/")[3] for i in xrange(studies_dset.shape[0])]
    chrs = [snp_group.name.split("/")[2] for i in xrange(studies_dset.shape[0])]
    array = np.column_stack((snps, snp_group['pvals'][:], chrs, snp_group['or'][:], studies_dset[:]))
    if info_array is None:
        info_array = array
    else:
        info_array = np.row_stack((info_array, array))
    return info_array


if __name__ == "__main__":
    main()
