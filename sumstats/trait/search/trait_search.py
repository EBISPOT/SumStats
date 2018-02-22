import os.path

import sumstats.trait.search.access.service as service
import sumstats.utils.utils as utils
from sumstats.trait.constants import *


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
        return self._search(self.max_size_of_trait, pval_interval=pval_interval)

    def search_study(self, study, pval_interval):
        total_study_size = self.searcher.get_study_size(self.trait, study)
        return self._search(total_study_size, study=study, pval_interval=pval_interval)

    def _search(self, max_size, study=None, pval_interval=None):
        iteration_size = self.size

        while self._not_traversed(max_size):
            if study is not None:
                self.searcher.query_for_study(trait=self.trait, study=study, start=self.start, size=iteration_size)
            else:
                self.searcher.query_for_trait(trait=self.trait, start=self.start, size=iteration_size)

            result_before_filtering = self.searcher.get_result()
            self._increase_search_index(min(iteration_size, len(result_before_filtering[REFERENCE_DSET])))

            # after search index is increased, we can apply restrictions
            self.searcher.apply_restrictions(pval_interval=pval_interval)

            self.datasets = utils.extend_dsets_with_subset(self.datasets, self.searcher.get_result())
            self.start = self.start + iteration_size
            iteration_size = self._next_iteration_size()

            if self._search_complete():
                break

        self.searcher.close_file()
        return self.datasets, self.index_marker

    def _not_traversed(self, max_size):
        return self.start < max_size

    def _increase_search_index(self, iteration_size):
        self.index_marker += iteration_size

    def _next_iteration_size(self):
        return self.size - len(self.datasets[REFERENCE_DSET])

    def _search_complete(self):
        return len(self.datasets[REFERENCE_DSET]) >= self.size