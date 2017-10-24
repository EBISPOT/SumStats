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
    myutils.argument_checker()
    args = myutils.argument_parser()
    query, trait, study, snp, chr, p_upper_limit, p_lower_limit, bp_upper_limit, bp_lower_limit = myutils.convert_args(args)

    search = Search(args.h5file)

    name_to_dataset = {}
    if query == 1:
        name_to_dataset = search.query_for_trait(trait)
    elif query == 2:
        name_to_dataset = search.query_for_study(trait, study)

    restrictions = []
    if snp is not None:
        restrictions.append(EqualityRestriction(snp, name_to_dataset[SNP_DSET]))
    if chr is not None:
        restrictions.append(EqualityRestriction(chr, name_to_dataset[CHR_DSET]))
    if p_upper_limit is not None or p_lower_limit is not None:
        restrictions.append(IntervalRestriction(p_lower_limit, p_upper_limit, name_to_dataset[MANTISSA_DSET]))
    if bp_upper_limit is not None or bp_lower_limit is not None:
        restrictions.append(IntervalRestriction(bp_lower_limit, bp_upper_limit, name_to_dataset[BP_DSET]))

    if restrictions:
        name_to_dataset = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
    print("Number of snp's retrieved", len(name_to_dataset[SNP_DSET]))
    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset][:10])


if __name__ == "__main__":
    main()
