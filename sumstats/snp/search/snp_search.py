import os.path

import sumstats.snp.search.access.service as service
import sumstats.utils.utils as utils
from sumstats.snp.constants import *


class SNPSearch:
    def __init__(self, snp, start, size, path=None):
        self.snp = snp
        self.start = start
        self.size = size
        if path is None:
            print("Retriever: setting default location for output files")
            path = "/output"
        self.path = path

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        self.index_marker = 0

        self.searcher = None
        for chromosome in range(1, 24):
            h5file = utils.create_file_path(path=self.path, dir_name="bysnp", file_name=chromosome)
            if not os.path.isfile(h5file):
                continue
            self.searcher = service.Service(h5file)
            if self.searcher.snp_in_file(snp):
                break
            else:
                self.searcher = None

        if self.searcher is None:
            raise ValueError("Variant does not exist in any chromosome!", snp)

    def search_snp(self, study=None, pval_interval=None):
        return self._search(study=study, pval_interval=pval_interval)

    def _search(self, study=None, pval_interval=None):
        iteration_size = self.size

        while True:
            self.searcher.query_for_snp(snp=self.snp, start=self.start, size=iteration_size)

            result_before_filtering = self.searcher.get_result()

            if self._traversed(result_before_filtering):
                break

            self._increase_search_index(result_before_filtering)

            # after search index is increased, we can apply restrictions
            self.searcher.apply_restrictions(study=study, pval_interval=pval_interval)

            self.datasets = utils.extend_dsets_with_subset(self.datasets, self.searcher.get_result())
            self.start = self.start + iteration_size
            iteration_size = self._next_iteration_size()

            if self._search_complete():
                break

        self.searcher.close_file()
        return self.datasets, self.index_marker

    def _traversed(self, result):
        return len(result[REFERENCE_DSET]) == 0

    def _increase_search_index(self, result):
        self.index_marker += len(result[REFERENCE_DSET])

    def _next_iteration_size(self):
        return self.size - len(self.datasets[REFERENCE_DSET])

    def _search_complete(self):
        return len(self.datasets[REFERENCE_DSET]) >= self.size
