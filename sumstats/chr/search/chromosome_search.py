import os.path

import sumstats.chr.search.access.service as service
import sumstats.utils.utils as utils
from sumstats.chr.constants import *


class ChromosomeSearch:
    def __init__(self, chromosome, start, size, path=None):
        self.chromosome = chromosome
        self.start = start
        self.size = size
        if path is None:
            print("Retriever: setting default location for output files")
            path = "/output"
        self.path = path

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        self.index_marker = 0

        self.h5file = utils.create_file_path(path=self.path, dir_name="bychr", file_name=chromosome)

        if not os.path.isfile(self.h5file):
            raise ValueError("Chromosome does not exist!", chromosome)
        self.searcher = service.Service(self.h5file)

    def search_chromosome(self):
        self.searcher.query_for_chromosome(chromosome=self.chromosome, start=self.start, size=self.size)
        result = self.searcher.get_result()
        self.searcher.close_file()
        return result, len(result[REFERENCE_DSET])

    def search_chromosome_block(self, bp_interval):
        self.searcher.query_chr_for_block_range(chromosome=self.chromosome, bp_interval=bp_interval, start=self.start, size=self.size)
        result = self.searcher.get_result()
        self.searcher.close_file()
        return result, len(result[REFERENCE_DSET])
