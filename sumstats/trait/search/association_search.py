import sumstats.explorer as ex
import sumstats.trait.search.access.trait_service as service
import sumstats.trait.search.trait_search as ts
import sumstats.utils.dataset_utils as utils
import sumstats.utils.filesystem_utils as fsutils
from sumstats.trait.constants import *
import logging
from sumstats.utils import register_logger
from sumstats.utils import properties_handler

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class AssociationSearch:
    def __init__(self, start, size, config_properties=None):
        self.starting_point = start
        self.start = start
        self.size = size

        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.trait_dir = self.properties.trait_dir

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = self.search_traversed = 0

    def get_all_associations(self, pval_interval=None):
        logger.info("Searching all associations for start %s and size %s", str(self.start), str(self.size))
        iteration_size = self.size
        available_traits = self._get_all_traits()
        for trait in available_traits:
            logger.debug(
                "Searching all associations for trait %s, start %s, and iteration size %s", trait, str(self.start),
                str(iteration_size))
            search_trait = ts.TraitSearch(trait=trait, start=self.start, size=iteration_size, config_properties=self.properties)
            result, current_trait_index = search_trait.search_trait(pval_interval)

            self._extend_datasets(result)
            self._calculate_total_traversal_of_search(trait=trait, current_trait_index=current_trait_index)
            self._increase_search_index(current_trait_index)

            if self._search_complete():
                logger.debug("Search completed for trait %s", trait)
                logger.info("Completed search for all associations. Returning index marker %s", str(self.index_marker))
                return self.datasets, self.index_marker

            iteration_size = self._next_iteration_size()
            logger.debug("Calculating next iteration start and size")
            self.start = self._next_start_index(current_search_index=current_trait_index)

            logger.info("Completed search for all associations. Returning index marker %s", str(self.index_marker))
        return self.datasets, self.index_marker

    def _get_all_traits(self):
        explorer = ex.Explorer(self.properties)
        return explorer.get_list_of_traits()

    def _next_iteration_size(self):
        return self.size - len(self.datasets[REFERENCE_DSET])

    def _increase_search_index(self, iteration_size):
        self.index_marker += iteration_size

    def _extend_datasets(self, result):
        self.datasets = utils.extend_dsets_with_subset(self.datasets, result)

    def _calculate_total_traversal_of_search(self, trait, current_trait_index):
        self.search_traversed += self._get_traversed_size(retrieved_index=current_trait_index, trait=trait)

    def _search_complete(self):
        return len(self.datasets[REFERENCE_DSET]) >= self.size

    def _get_traversed_size(self, retrieved_index, trait):
        if retrieved_index == 0:
            h5file = fsutils.create_h5file_path(self.search_path, dir_name=self.trait_dir, file_name=trait)
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