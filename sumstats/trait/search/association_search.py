
import sumstats.explorer as ex
import sumstats.trait.search.access.trait_service as service
import sumstats.trait.search.trait_search as ts
import sumstats.utils.utils as utils
from sumstats.trait.constants import *


class AssociationSearch:
    def __init__(self, start, size, path=None):
        self.starting_point = start
        self.start = start
        self.size = size
        if path is None:
            print("Retriever: setting default location for output files")
            path = "/output"

        self.path = path
        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        self.trait_list = []
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = self.search_traversed = 0

    def get_all_associations(self, pval_interval=None):
        iteration_size = self.size
        available_traits = self._get_all_traits()

        for trait in available_traits:
            search_trait = ts.TraitSearch(trait=trait, start=self.start, size=iteration_size, path=self.path)
            result, current_trait_index = search_trait.search_trait(pval_interval)

            self._extend_datasets(trait=trait, result=result)
            self._calculate_total_traversal_of_search(trait=trait, current_trait_index=current_trait_index)
            self._increase_search_index(current_trait_index)

            if self._search_complete():
                self.datasets['trait'] = self.trait_list
                return self.datasets, self.index_marker

            iteration_size = self._next_iteration_size()
            self.start = self._next_start_index(current_search_index=current_trait_index)

        return self.datasets, self.index_marker

    def _get_all_traits(self):
        explorer = ex.Explorer(self.path)
        return explorer.get_list_of_traits()

    def _next_iteration_size(self):
        return self.size - len(self.datasets[REFERENCE_DSET])

    def _increase_search_index(self, iteration_size):
        self.index_marker += iteration_size

    def _extend_datasets(self, trait, result):
        self.datasets = utils.extend_dsets_with_subset(self.datasets, result)
        self.trait_list.extend([trait for _ in range(len(result[REFERENCE_DSET]))])

    def _calculate_total_traversal_of_search(self, trait, current_trait_index):
        self.search_traversed += self._get_traversed_size(retrieved_index=current_trait_index, trait=trait)

    def _search_complete(self):
        return len(self.datasets[REFERENCE_DSET]) >= self.size

    def _get_traversed_size(self, retrieved_index, trait):
        if retrieved_index == 0:
            h5file = utils.create_file_path(self.path, dir_name="bytrait", file_name=trait)
            searcher = service.TraitService(h5file)
            trait_size = searcher.get_trait_size(trait)
            searcher.close_file()
            return trait_size
        return retrieved_index

    def _next_start_index(self, current_search_index):
        if current_search_index == self.search_traversed:
            # we have retrieved the trait from start to end
            # retrieving next trait from it's beginning
            return 0
        new_start = self.start - self.search_traversed + current_search_index
        if new_start < 0:
            return self.start + current_search_index
        return new_start