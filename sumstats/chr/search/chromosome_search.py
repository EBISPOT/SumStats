import os.path

import sumstats.chr.search.access.service as service
import sumstats.utils.utils as utils
from sumstats.chr.constants import *
from sumstats.utils import  search
from sumstats.errors.error_classes import *


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
            raise NotFoundError("Chromosome " + str(chromosome))
        self.searcher = service.Service(self.h5file)

    def search_chromosome(self, study=None, pval_interval=None):
        max_size = self.searcher.get_chromosome_size(chromosome=self.chromosome)
        method_arguments = {'chromosome': self.chromosome}
        search_constructor = {'object': self.searcher, 'method': 'query_for_chromosome', 'args': method_arguments}
        restrictions = {'pval_interval': pval_interval, 'study': study}
        return search.general_search(search_obj=self, max_size=max_size,
                                     search_constructor=search_constructor, restriction_dictionary=restrictions)

    def search_chromosome_block(self, bp_interval, study=None, pval_interval=None):
        max_size = self.searcher.get_block_range_size(chromosome=self.chromosome, bp_interval=bp_interval)
        method_arguments = {'chromosome': self.chromosome, 'bp_interval': bp_interval}
        search_constructor = {'object': self.searcher, 'method': 'query_chr_for_block_range', 'args': method_arguments}
        restrictions = {'pval_interval': pval_interval, 'study': study}
        return search.general_search(search_obj=self, max_size=max_size,
                                     search_constructor=search_constructor, restriction_dictionary=restrictions)

