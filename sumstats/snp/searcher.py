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
import sumstats.utils.argument_utils as au


class Search():

    def __init__(self, h5file):
        self.h5file = h5file
        # Open the file with read permissions
        self.f = h5py.File(h5file, 'r')
        self.name_to_dset = {}

    def snp_in_file(self, snp):
        return snp in self.f

    def query_for_snp(self, snp):
        snp_group = gu.get_group_from_parent(self.f, snp)
        self.name_to_dset = myutils.get_dsets_from_group(snp_group)

    def apply_restrictions(self, snp=None, study=None, chr=None, pval_interval=None, bp_interval=None):
        restrictions = utils.create_restrictions(self.name_to_dset, snp=snp, study=study, chr=chr, pval_interval=pval_interval, bp_interval=bp_interval)
        if restrictions:
            self.name_to_dset = utils.filter_dsets_with_restrictions(self.name_to_dset, restrictions)

    def get_result(self):
        return self.name_to_dset


def main():
    args = au.search_argument_parser()
    trait, study, chr, bp_interval, snp, pval_interval = au.convert_search_args(args)

    search = Search(args.h5file)

    search.query_for_snp(snp)

    search.apply_restrictions(study=study, pval_interval=pval_interval)

    name_to_dataset = search.get_result()

    print("Number of studies retrieved", len(name_to_dataset[STUDY_DSET]))
    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset][:10])


if __name__ == "__main__":
    main()