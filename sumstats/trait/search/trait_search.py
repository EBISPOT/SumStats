import os.path

import sumstats.trait.search.access.service as service
import sumstats.utils.utils as utils
from sumstats.trait.constants import *
from sumstats.utils import search


class TraitSearch:
    def __init__(self, trait, start, size, path=None):
        self.trait = trait
        self.start = start
        self.size = size
        if path is None:
            print("Retriever: setting default location for output files")
            path = "/output"
        self.path = path

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = 0

        self.h5file = utils.create_file_path(self.path, dir_name="bytrait", file_name=trait)
        if not os.path.isfile(self.h5file):
            raise ValueError("Trait does not exist in file!", trait)
        self.searcher = service.Service(self.h5file)
        self.max_size_of_trait = self.searcher.get_trait_size(self.trait)

    def search_trait(self, pval_interval=None):
        method_arguments = {'trait': self.trait}
        search_constructor = {'object': self.searcher, 'method': 'query_for_trait', 'args': method_arguments}
        restrictions = {'pval_interval': pval_interval}
        return search.general_search(search_obj=self, max_size=self.max_size_of_trait, search_constructor=search_constructor, restriction_dictionary=restrictions)

    def search_study(self, study, pval_interval):
        method_arguments = {'trait': self.trait, 'study': study}
        search_constructor = {'object': self.searcher, 'method': 'query_for_study', 'args': method_arguments}
        total_study_size = self.searcher.get_study_size(self.trait, study)
        restrictions = {'pval_interval': pval_interval}
        return search.general_search(search_obj=self, max_size=total_study_size, search_constructor=search_constructor, restriction_dictionary=restrictions)
