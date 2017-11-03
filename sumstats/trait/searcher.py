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
from sumstats.trait.constants import *
import sumstats.utils.group as gu
import sumstats.utils.utils as utils
import sumstats.utils.argument_utils as au


class Search():
    def __init__(self, h5file):
        self.h5file = h5file
        # Open the file with read permissions
        self.f = h5py.File(h5file, 'r')
        self.name_to_dset = {}

    def query_for_trait(self, trait):
        trait_group = gu.get_group_from_parent(self.f, trait)
        self.name_to_dset = myutils.get_dsets_from_trait_group(trait_group)

    def query_for_study(self, trait, study):
        trait_group = gu.get_group_from_parent(self.f, trait)
        study_group = gu.get_group_from_parent(trait_group, study)

        self.name_to_dset = myutils.get_dsets_from_group(study, study_group)

    def apply_restrictions(self, snp=None, study=None, chr=None, pval_interval=None, bp_interval=None):
        restrict_dict = {}
        if SNP_DSET in self.name_to_dset:
            restrict_dict[SNP_DSET] = snp
        if STUDY_DSET in self.name_to_dset:
            restrict_dict[STUDY_DSET] = study
        if CHR_DSET in self.name_to_dset:
            restrict_dict[CHR_DSET] = chr
        if MANTISSA_DSET in self.name_to_dset:
            restrict_dict[MANTISSA_DSET] = pval_interval
        if BP_DSET in self.name_to_dset:
            restrict_dict[BP_DSET] = bp_interval

        restrictions = utils.create_restrictions(self.name_to_dset, restrict_dict)
        if restrictions:
            self.name_to_dset = utils.filter_dsets_with_restrictions(self.name_to_dset, restrictions)

    def get_result(self):
        return self.name_to_dset

    def list_traits(self):
        trait_groups = gu.get_all_groups_from_parent(self.f)
        return [trait_group.name.strip("/") for trait_group in trait_groups]

    def list_studies(self):
        trait_groups = gu.get_all_groups_from_parent(self.f)
        study_groups = []

        for trait_group in trait_groups:
            study_groups.extend(gu.get_all_groups_from_parent(trait_group))
        return [study_group.name.strip("/").replace("/",": ") for study_group in study_groups]




def main():
    args = au.search_argument_parser()
    trait, study, chr, bp_interval, snp, pval_interval = au.convert_search_args(args)

    search = Search(args.h5file)

    if study is None:
        search.query_for_trait(trait)
    else:
        search.query_for_study(trait, study)

    search.apply_restrictions(snp=snp, chr=chr, pval_interval=pval_interval, bp_interval=bp_interval)

    name_to_dataset = search.get_result()

    print("Number of snp's retrieved", len(name_to_dataset[SNP_DSET]))
    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset][:10])


if __name__ == "__main__":
    main()
