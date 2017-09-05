"""
    Data stored in the hierarchy of Trait/Study/SNP/DATA
    where DATA:

    vector that has in position 0 the p-value, in position 1 the chromosome, in position 2 the OR value
    for this study/snp association
    we can add more data if we want to to this vector

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
    trait_group = f.get(trait)
    if trait_group is not None:
        return retrieve_trait_info(trait_group)
    else:
        print "Trait does not exist!", trait
        exit(1)


def all_study_info(f, trait, study):
    print "Retrieving info for study:", study
    study_group = f.get(trait + "/" + study)
    if study_group is not None:
        return retrieve_study_group_info(study_group)
    else:
        print "Not valid trait/study combination"
        exit(1)


def all_chromosome_info(f, chromosome, trait):
    print "Retrieving info for chromosome:", chromosome
    if trait is None:
        info_array = retrieve_file_info(f)
    else:
        trait_group = f.get(trait)
        if trait_group is not None:
            info_array = retrieve_trait_info(trait_group)

    print info_array[:,2]
    chr_np = np.array(info_array[:,2], dtype=float)
    mask = chr_np == float(chromosome)

    return info_array[mask]


def all_snp_info(f, snp, trait):
    info_array = None
    if trait is None:
        for x, trait_group in f.iteritems():
            if info_array is None:
                info_array = all_snp_info_from_trait(snp, trait_group)
            else:
                info_array = np.row_stack((info_array, all_snp_info_from_trait(snp, trait_group)))
    else:
        trait_group = f.get(trait)
        if trait_group is not None:
            info_array = all_snp_info_from_trait(snp, trait_group)
        else:
            print "Trait does not exist"
            exit(1)
    return info_array


def all_snp_info_from_trait(snp, trait_group):
    info_array = None
    for study_group_name, study_group in trait_group.iteritems():
        snp_dataset = study_group.get(snp)
        names = snp_dataset.name.split("/")
        if snp_dataset is not None:
            row = retrieve_snp_dset_info(names[3], snp_dataset, study_group_name)
            if info_array is None:
                info_array = row
            else:
                info_array = np.row_stack((info_array, row))
    return info_array


def retrieve_file_info(f):
    info_array = None
    for x, trait_group in f.iteritems():
        if info_array is None:
            info_array = retrieve_trait_info(trait_group)
        else:
            info_array = np.row_stack((info_array, retrieve_trait_info(trait_group)))
    return info_array


def retrieve_trait_info(trait_group):
    info_array = None
    print "looping through trait"
    for x, study_group in trait_group.iteritems():
        if info_array is None:
            info_array = retrieve_study_group_info(study_group)
        else:
            info_array = np.row_stack((info_array, retrieve_study_group_info(study_group)))
    return info_array


def retrieve_study_group_info(study_group):
    info_array = None
    for snp_name, snp_dataset in study_group.iteritems():
        row = retrieve_snp_dset_info(snp_name, snp_dataset, study_group.name)
        if info_array is None:
            info_array = row
        else:
            info_array = np.row_stack((info_array, row))
    return info_array


def retrieve_snp_dset_info(snp_name, snp_dataset, study_group_name):
    return np.array([[snp_name, snp_dataset[0], snp_dataset[1], snp_dataset[2], study_group_name]])


if __name__ == "__main__":
    main()
