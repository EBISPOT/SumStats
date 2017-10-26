"""
    Stored as /SNP/DATA
    Where DATA:
    under each directory we store 3 (or more) vectors
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'bp' list will hold the baise pair location that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    for a SNP group:
    study[0], mantissa[0], exp[0], and bp[0] hold the information for this SNP for study[0]

    Query: query for specific SNP that belongs

    Can filter based on p-value thresholds and/or specific study
"""

import sumstats.snp.query_utils as myutils
from sumstats.utils.restrictions import *
from sumstats.snp.constants import *
import sumstats.utils.group as gu
import sumstats.utils.utils as utils


def query_for_snp(parent_group, snp):
    snp_group = gu.get_group_from_parent(parent_group, snp)
    return myutils.get_dsets_from_group(snp_group)


def main():
    args = myutils.argument_parser()
    snp, study, pval_interval = myutils.convert_args(args)

    # open h5 file in read mode
    file = h5py.File(args.h5file, mode="r")

    name_to_dataset = query_for_snp(file, snp)

    restrictions = []
    if study is not None:
        restrictions.append(EqualityRestriction(study, name_to_dataset[STUDY_DSET]))
    if not pval_interval.is_set():
        restrictions.append(IntervalRestriction(pval_interval.floor(), pval_interval.ceil(), name_to_dataset[MANTISSA_DSET]))

    if restrictions:
        name_to_dataset = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)

    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset][:10])


if __name__ == "__main__":
    main()