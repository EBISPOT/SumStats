"""
Utils useful for querying
"""

import argparse
from sumstats.snp.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu
from sumstats.utils.interval import *


def get_dsets_from_group(group):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    return gu.extend_dsets_for_group(group=group, name_to_dataset=name_to_dataset)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-snp', help='The SNP I am looking for', required=True)
    parser.add_argument('-study', help='Filter results for a specific study')
    parser.add_argument('-pval', help='Filter by pval threshold: -pval floor:ceil')
    return parser.parse_args()


def convert_args(args):
    snp = args.snp
    study = args.study

    pval_interval = args.pval
    pval_interval = FloatInterval().set_string_tuple(pval_interval)

    return snp, study, pval_interval
