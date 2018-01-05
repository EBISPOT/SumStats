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

import sumstats.trait.query as query
from sumstats.trait.constants import *
import sumstats.utils.group as gu
import sumstats.utils.utils as utils


class Search():
    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.name_to_dset = {}

    def query_for_all_associations(self, start, size):
        self.name_to_dset = query.get_dsets_from_file(self.file, start, size)

    def query_for_trait(self, trait, start, size):
        trait_group = gu.get_group_from_parent(self.file, trait)
        self.name_to_dset = query.get_dsets_from_trait_group(trait_group, start, size)

    def query_for_study(self, trait, study, start, size):
        trait_group = gu.get_group_from_parent(self.file, trait)
        study_group = gu.get_group_from_parent(trait_group, study)

        self.name_to_dset = query.get_dsets_from_group_directly(study, study_group, start, size)

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
        trait_groups = gu.get_all_groups_from_parent(self.file)
        return [trait_group.name.strip("/") for trait_group in trait_groups]

    def list_studies(self):
        trait_groups = gu.get_all_groups_from_parent(self.file)
        study_groups = []

        for trait_group in trait_groups:
            study_groups.extend(gu.get_all_groups_from_parent(trait_group))
        return [study_group.name.strip("/").replace("/",": ") for study_group in study_groups]

    def close_file(self):
        self.file.close()
