import argparse
from sumstats.trait.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def get_dsets_from_file(f):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

    for trait, trait_group in f.items():
        name_to_datastet_for_trait = get_dsets_from_trait_group(trait_group)
        for dset_name, dataset in name_to_dataset.items():
            dataset.extend(name_to_datastet_for_trait[dset_name])

    return name_to_dataset


def get_dsets_from_trait_group(trait_group):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

    for study, study_group in trait_group.items():
        name_to_dataset_for_study = get_dsets_from_group(study, study_group)
        for dset_name, dataset in name_to_dataset.items():
            dataset.extend(name_to_dataset_for_study[dset_name])
    return name_to_dataset


def get_dsets_from_group(study, study_group):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    return gu.extend_dsets_for_group(group_name=study, group=study_group,
                                     name_to_dataset=name_to_dataset,
                                     missing_dset=STUDY_DSET,
                                     existing_dset=SNP_DSET)


def argument_checker():
    args = argument_parser()
    if args.query == "1":
        pass
    elif args.query == "2":
        if args.study is None:
            raise ValueError("Can't retrieve study data without study name")
    else:
        raise ValueError("Wrong input")


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help='The name of the HDF5 file', required=True)
    parser.add_argument('-query', help='The nmber of the query to perform', required=True)
    parser.add_argument('-trait', help='The trait I am looking for', required=True)
    parser.add_argument('-study', help='The study I am looking for')
    parser.add_argument('-snp', help='Filter by SNP')
    parser.add_argument('-chr', help='Filter by chromosome')
    parser.add_argument('-pu', help='Filter with upper limit for the p-value')
    parser.add_argument('-pl', help='Filter with lower limit for the p-value')
    parser.add_argument('-bu', help='Filter with upper limit for the base pair location')
    parser.add_argument('-bl', help='Filter with lower limit for the base pair location')

    return parser.parse_args()


def convert_args(args):
    query = int(args.query)
    trait = args.trait
    study = args.study
    snp = args.snp
    chr = args.chr
    if chr is not None:
        chr = int(chr)
    p_upper_limit = args.pu
    if p_upper_limit is not None:
        p_upper_limit = float(p_upper_limit)
    p_lower_limit = args.pl
    if p_lower_limit is not None:
        p_lower_limit = float(p_lower_limit)

    bp_upper_limit = args.bu
    if bp_upper_limit is not None:
        bp_upper_limit = int(bp_upper_limit)
    bp_lower_limit = args.bl
    if bp_lower_limit is not None:
        bp_lower_limit = int(bp_lower_limit)

    return query, trait, study, snp, chr, p_upper_limit, p_lower_limit, bp_upper_limit, bp_lower_limit
