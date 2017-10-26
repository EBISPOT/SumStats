"""
    Data is stored in the hierarchy of /Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    'snp' list will hold the snp ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'chr' list will hold the chromosome that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    snp[0], mantissa[0], exp[0], and chr[0] hold the information for SNP 0

    Query 1: Retrieve all information for trait: input = query number (1) and trait name
    Query 2: Retrieve all the information for a study: input = query number (2) and study name and trait name

    Can filter based on p-value thresholds, bp position thresholds, SNP, CHR
"""

import sumstats.trait.query_utils as myutils
from sumstats.utils.restrictions import *
from sumstats.trait.constants import *
import sumstats.utils.group as gu
import sumstats.utils.utils as utils


class Search():
    def __init__(self, h5file):
        self.h5file = h5file
        # Open the file with read permissions
        self.f = h5py.File(h5file, 'r')

    def query_for_trait(self, trait):
        trait_group = gu.get_group_from_parent(self.f, trait)
        return myutils.get_dsets_from_trait_group(trait_group)

    def query_for_study(self, trait, study):
        trait_group = gu.get_group_from_parent(self.f, trait)
        study_group = gu.get_group_from_parent(trait_group, study)

        return myutils.get_dsets_from_group(study, study_group)


def main():
    args = myutils.argument_parser()
    trait, study, snp, chr, pval_interval, bp_interval = myutils.convert_args(args)

    search = Search(args.h5file)

    if study is None:
        name_to_dataset = search.query_for_trait(trait)
    else:
        name_to_dataset = search.query_for_study(trait, study)

    restrictions = []
    if snp is not None:
        restrictions.append(EqualityRestriction(snp, name_to_dataset[SNP_DSET]))
    if chr is not None:
        restrictions.append(EqualityRestriction(chr, name_to_dataset[CHR_DSET]))
    if not pval_interval.is_set():
        restrictions.append(IntervalRestriction(pval_interval.floor(), pval_interval.ceil(), name_to_dataset[MANTISSA_DSET]))
    if not bp_interval.is_set():
        restrictions.append(IntervalRestriction(bp_interval.floor(), bp_interval.ceil(), name_to_dataset[BP_DSET]))

    if restrictions:
        name_to_dataset = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
    print("Number of snp's retrieved", len(name_to_dataset[SNP_DSET]))
    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset][:10])


if __name__ == "__main__":
    main()
