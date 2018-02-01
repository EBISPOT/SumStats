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
        self.search_index = 0

        self.h5file = utils.create_file_path(self.path, dir_name="bytrait", file_name=trait)
        if not os.path.isfile(self.h5file):
            raise ValueError("Trait does not exist in file!", trait)
        self.searcher = service.Service(self.h5file)
        self.max_size_of_trait = self.searcher.get_trait_size(self.trait)

    def search_trait(self, pval_interval=None):
        iteration_size = self.size

        while self._trait_not_traversed():
            self.searcher.query_for_trait(trait=self.trait, start=self.start, size=iteration_size)
            self._increase_search_index(self.searcher.get_result())

            # after search index is increased, we can apply restrictions
            self.searcher.apply_restrictions(pval_interval=pval_interval)

            self.datasets = utils.extend_dsets_with_subset(self.datasets, self.searcher.get_result())

            self.start = self.start + self.size
            iteration_size = self._next_iteration_size()

            if self._search_complete():
                break

        self.searcher.close_file()
        return self.datasets, self.search_index

    def search_study(self, study, pval_interval):
        searcher = service.Service(self.h5file)
        searcher.query_for_study(trait=self.trait, study=study, start=self.start, size=self.size)
        result = searcher.get_result()
        searcher.close_file()
        return result

    def _trait_not_traversed(self):
        return self.start < self.max_size_of_trait

    def _increase_search_index(self, result):
        self.search_index += len(result[REFERENCE_DSET])

    def _next_iteration_size(self):
        return self.size - len(self.datasets[REFERENCE_DSET])

    def _search_complete(self):
        return len(self.datasets[REFERENCE_DSET]) >= self.size