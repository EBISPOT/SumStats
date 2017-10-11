"""
    Data is stored in the hierarchy of Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    snparray will hold the snp ids
    pvals will hold each snps pvalue for this study
    chr will hold each snps position
    or_array will hold each snps odds ratio for this study
    we can add any other information that we want

    the positions in the vectors correspond to each other
    snparray[0], pvals[0], chr[0], and or_array[0] hold the information for SNP 0

    Query 1: Retrieve all information for trait: input = query number (1) and trait name
    Query 2: Retrieve all the information for a study: input = query number (2) and study name and trait name

    If a p-value threshold is given, all returned values need to be restricted to this threshold
"""

import h5py
import numpy as np
from sumstats.utils import utils
import sumstats.trait.query_utils as myutils

TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr', 'or', 'bp', 'effect', 'other']
TO_STORE_DSETS = ['snp', 'pval', 'chr', 'or', 'bp', 'effect', 'other']
TO_QUERY_DSETS = ['snp', 'pval', 'chr', 'or', 'study', 'bp', 'effect', 'other']
SNP_DSET = 'snp'
BP_DSET = 'bp'
PVAL_DSET = 'pval'
CHR_DSET = 'chr'


class Search():
    def __init__(self, h5file):
        self.h5file = h5file
        # Open the file with read/write permissions and create if it doesn't exist
        self.f = h5py.File(h5file, 'r')

    def query_for_trait(self, trait):
        trait_group = utils.get_group_from_parent(self.f, trait)
        return myutils.get_dsets_from_trait_group(trait_group, TO_QUERY_DSETS)

    def query_for_study(self, trait, study):
        trait_group = utils.get_group_from_parent(self.f, trait)
        study_group = utils.get_group_from_parent(trait_group, study)

        name_to_dataset = {}

        for dset_name in TO_QUERY_DSETS:
            name_to_dataset[dset_name] = np.array(myutils.get_dset_from_group(dset_name, study_group, study))

        return name_to_dataset



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

    dset_name_to_restriction = {}
    dset_name_to_restriction['snp'] = snp
    dset_name_to_restriction['chr'] = chr
    dset_name_to_restriction['pval'] = (p_lower_limit, p_upper_limit)
    dset_name_to_restriction['bp'] = (bp_lower_limit, bp_upper_limit)

    name_to_dataset = utils.filter_dsets_with_restrictions(name_to_dataset, dset_name_to_restriction)

    for dset in name_to_dataset:
        print(dset)
        print(name_to_dataset[dset])


if __name__ == "__main__":
    main()
