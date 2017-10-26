import argparse
from sumstats.trait.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu
from sumstats.utils.interval import *

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
    return gu.extend_dsets_for_group_missing(missing_value=study, group=study_group,
                                             name_to_dataset=name_to_dataset,
                                             missing_dset=STUDY_DSET,
                                             existing_dset=SNP_DSET)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help='The name of the HDF5 file', required=True)
    parser.add_argument('-trait', help='The trait I am looking for', required=True)
    parser.add_argument('-study', help='The study I am looking for')
    parser.add_argument('-snp', help='Filter by SNP')
    parser.add_argument('-chr', help='Filter by chromosome')
    parser.add_argument('-pval', help='Filter by pval threshold: -pval floor:ceil')
    parser.add_argument('-bp', help='Filter with baise pair location threshold: -bp floor:ceil')

    return parser.parse_args()


def convert_args(args):
    trait = args.trait
    study = args.study
    snp = args.snp

    chr = args.chr
    if chr is not None:
        chr = int(chr)

    pval_interval = args.pval
    pval_interval = FloatInterval().set_string_tuple(pval_interval)

    bp_interval = args.bp
    bp_interval = IntInterval().set_string_tuple(bp_interval)

    return trait, study, snp, chr, pval_interval, bp_interval
