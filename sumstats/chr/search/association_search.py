from multiprocessing import Pool

import sumstats.explorer as ex
from sumstats.trait.search.access import trait_service
import sumstats.trait.search.trait_search as ts
from sumstats.chr.search.access import chromosome_service
import sumstats.chr.search.chromosome_search as cs
import sumstats.utils.dataset_utils as utils
import sumstats.utils.filesystem_utils as fsutils
from sumstats.chr.constants import *
import logging
from sumstats.utils import register_logger
from sumstats.utils import properties_handler

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class AssociationSearch:
    def __init__(self, start, size, config_properties=None, studies=None):
        self.starting_point = start
        self.start = start
        self.size = size
        self.studies = [studies]

        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.chr_dir = self.properties.chr_dir

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = self.search_traversed = 0

    def search_associations(self, pval_interval=None):
        """
        Traverses the chromosomes and studies therein and retrieves the data stored in their datasets.
        It traverses the datasets of the first trait before it continues to the next trait's datasets.
        If a trait will be skipped or not is determined by each trait's search methods.
        :param pval_interval: filter by p-value interval if not None
        :return: a dictionary containing the dataset names and slices of the datasets
        """
        logger.info("Searching all associations for start %s, size %s, pval_interval %s",
                    str(self.start), str(self.size), str(pval_interval))
        self.iteration_size = self.size
        available_chroms = self._get_all_chroms()

        for chrom in available_chroms:
            while not self._search_complete():
                if self.studies[0] is not None:
                    for study in self.studies:
                        self.perform_search(pval_interval=pval_interval, chrom=chrom, study=study)
                else:
                    self.perform_search(pval_interval=pval_interval, chrom=chrom)

        return self.datasets, self.index_marker


    def perform_search(self, pval_interval=None, chrom=None, study=None):
        logger.debug(
            "Searching all associations for chrom %s, start %s, and iteration size %s", chrom,
            str(self.start),
            str(self.iteration_size))
        print("search chrom")
        search_chrom = cs.ChromosomeSearch(chromosome=chrom, start=self.start, size=self.iteration_size,
                                           config_properties=self.properties)
        result, current_chrom_index = search_chrom.search_chromosome(study=study,
                                                                     pval_interval=pval_interval)

        print("finished search chrom")
        self._extend_datasets(result)
        self._calculate_total_traversal_of_search(chrom=chrom, current_chrom_index=current_chrom_index)
        self._increase_search_index(current_chrom_index)

        if self._search_complete():
            print("search complete")
            logger.debug("Search completed for trait %s", chrom)
            logger.info("Completed search for all associations. Returning index marker %s",
                        str(self.index_marker))
            return self.datasets, self.index_marker

        self.iteration_size = self._next_iteration_size()
        print("it: " + str(self.iteration_size))
        logger.debug("Calculating next iteration start and size...")
        self.start = self._next_start_index(current_search_index=current_chrom_index)

        logger.info("Completed search for all associations. Returning index marker %s",
                    str(self.index_marker))

    def _get_all_traits(self):
        explorer = ex.Explorer(self.properties)
        return explorer.get_list_of_traits()

    def _get_all_chroms(self):
        explorer = ex.Explorer(self.properties)
        return explorer.get_list_of_chroms()

    def _next_iteration_size(self):
        return self.size - len(self.datasets[REFERENCE_DSET])

    def _increase_search_index(self, iteration_size):
        self.index_marker += iteration_size

    def _extend_datasets(self, result):
        self.datasets = utils.extend_dsets_with_subset(self.datasets, result)

    def _calculate_total_traversal_of_search(self, chrom, current_chrom_index):
        self.search_traversed += self._get_traversed_size(retrieved_index=current_chrom_index, chrom=chrom)

    def _search_complete(self):
        return len(self.datasets[REFERENCE_DSET]) >= self.size

    def _get_traversed_size(self, retrieved_index, chrom):
        if retrieved_index == 0:
            h5file = fsutils.create_h5file_path(self.search_path, dir_name=self.chrom_dir, file_name=chrom)
            service = chromosome_service.ChromosomeService(h5file)
            chrom_size = service.get_chromosome_size(chrom)
            service.close_file()
            return chrom_size
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