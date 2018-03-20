import os.path

import sumstats.snp.search.access.service as service
import sumstats.utils.utils as utils
from sumstats.snp.constants import *
from sumstats.utils import search
from sumstats.errors.error_classes import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class SNPSearch:
    def __init__(self, snp, start, size, path=None, chromosome=None):
        self.snp = snp
        self.chromosome = chromosome
        self.start = start
        self.size = size
        if path is None:
            print("Retriever: setting default location for output files")
            path = "/output"
        self.path = path

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        self.index_marker = 0

        if chromosome is None:
            self.searcher = self._calculate_searcher()
        else:
            self.searcher = self._get_searcher()

    def search_snp(self, study=None, pval_interval=None):
        logger.info("Searching for variant %s", self.snp)
        max_size = self.searcher.get_snp_size(self.snp)
        method_arguments = {'snp': self.snp}
        restrictions = {'pval_interval': pval_interval, 'study': study}
        return search.general_search(search_obj=self, max_size=max_size,
                                     arguments=method_arguments, restriction_dictionary=restrictions)

    def _calculate_searcher(self):
        logger.debug("Calculating chromosome for variant %s...", self.snp)
        for chromosome in range(1, 24):
            h5file = utils.create_h5file_path(path=self.path, dir_name="bysnp", file_name=chromosome)
            if not os.path.isfile(h5file):
                continue
            self.searcher = service.Service(h5file)
            if self.searcher.snp_in_file(self.snp):
                logger.debug("Variant %s found in chromosome %s", self.snp, str(chromosome))
                break
            self.searcher = None

        if self.searcher is None:
            logger.debug("Variant %s not found in any chromosome!", self.snp)
            raise NotFoundError("Variant " + self.snp)
        return self.searcher

    def _get_searcher(self):
        h5file = utils.create_h5file_path(path=self.path, dir_name="bysnp", file_name=self.chromosome)
        if not os.path.isfile(h5file):
            logger.debug(
                "Chromosome %s given for variant %s doesn't exist!", str(self.chromosome), self.snp)
            raise NotFoundError("Chromosome " + str(self.chromosome))
        return service.Service(h5file)