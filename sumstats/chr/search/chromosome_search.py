import os.path

import sumstats.chr.search.access.chromosome_service as service
import sumstats.utils.utils as utils
from sumstats.chr.constants import *
from sumstats.utils import  search
from sumstats.errors.error_classes import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


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
        self.searcher = service.ChromosomeService(self.h5file)

    def search_chromosome(self, study=None, pval_interval=None):
        logger.info("Searching for chromosome %s", str(self.chromosome))
        max_size = self.searcher.get_chromosome_size(chromosome=self.chromosome)
        method_arguments = {'chromosome': self.chromosome}
        restrictions = {'pval_interval': pval_interval, 'study': study}
        return search.general_search(search_obj=self, max_size=max_size,
                                     arguments=method_arguments, restriction_dictionary=restrictions)
