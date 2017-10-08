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


class Search():
    def __init__(self, h5file):
        self.h5file = h5file
        # Open the file with read/write permissions and create if it doesn't exist
        self.f = h5py.File(h5file, 'r')

    def query_for_trait(self, trait):
        trait_group = utils.get_group_from_parent(self.f, trait)
        return myutils.get_dsets_from_trait_group(trait_group, names_of_dsets)

    def query_for_study(self, trait, study):
        trait_group = utils.get_group_from_parent(self.f, trait)
        study_group = utils.get_group_from_parent(trait_group, study)

        # initialize dictionary of datasets
        dictionary_of_dsets = {}

        for dset_name in names_of_dsets:
            dictionary_of_dsets[dset_name] = np.array(myutils.get_dset_from_group(dset_name, study_group, study))

        return dictionary_of_dsets


names_of_dsets = ["snp", "pval", "chr", "or", "study", "bp", "effect", "other"]


def main():
    myutils.argument_checker()
    args = myutils.argument_parser()

    search = Search(args.h5file)

    query = int(args.query)
    trait = args.trait
    study = args.study
    snp = args.snp
    chr = args.chr
    if chr is not None:
        chr = int(chr)
    upper_limit = args.pu
    if upper_limit is not None:
        upper_limit = float(upper_limit)
    lower_limit = args.pl
    if lower_limit is not None:
        lower_limit = float(lower_limit)

    if query == 1:
        # info_array = all_trait_info(f, args.trait)
        dictionary_of_dsets = search.query_for_trait(trait)
    elif query == 2:
        dictionary_of_dsets = search.query_for_study(trait, study)

    mask = utils.cutoff_mask(dictionary_of_dsets["pval"], upper_limit, lower_limit)

    if mask is not None:
        dictionary_of_dsets = utils.filter_dictionary_by_mask(dictionary_of_dsets, mask)

    for dset in dictionary_of_dsets:
        print(dset)
        print(dictionary_of_dsets[dset])


if __name__ == "__main__":
    main()
