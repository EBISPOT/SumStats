import sumstats.snp.search.access.service as service
import sumstats.utils.utils as utils
from sumstats.snp.constants import *
from sumstats.utils import search
from sumstats.errors.error_classes import *
import logging
from sumstats.utils import register_logger
from multiprocessing import Pool
from sumstats.utils import properties_handler

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class SNPSearch:
    def __init__(self, snp, start, size, config_properties=None, chromosome=None):
        self.snp = snp
        self.chromosome = chromosome
        self.start = start
        self.size = size

        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)

        self.chr_dir = self.properties.chr_dir
        self.snp_dir = self.properties.snp_dir
        self.bp_step = self.properties.bp_step

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

        for chromosome in range(1, 25):
            self.searcher = self._calculate_searcher_for_chromosome(chromosome)
            if self.searcher is not None:
                return self.searcher
        # if not returned yet, not found
        logger.debug("Variant %s not found in any chromosome!", self.snp)
        raise NotFoundError("Variant " + self.snp)

    def _calculate_searcher_for_chromosome(self, chromosome):
        try:
            h5file = self._location_for_snp_in_chromosome(chromosome)
        except NotFoundError:
            return None
        logger.debug("Variant %s found in chromosome %s", self.snp, str(chromosome))
        return service.Service(h5file)

    def _get_searcher(self):
        h5file = self._location_for_snp_in_chromosome(self.chromosome)
        return service.Service(h5file)

    def _location_for_snp_in_chromosome(self, chromosome):
        dir_name = utils.join(self.snp_dir, str(chromosome))
        if not utils.is_valid_dir_path(path=self.search_path, dir_name=dir_name):
            logger.debug(
                "Chromosome %s given for variant %s doesn't exist!", str(self.chromosome), self.snp)
            raise NotFoundError("Chromosome " + str(self.chromosome))
        h5files = utils.get_h5files_in_dir(path=self.search_path, dir_name=dir_name)

        snps = [self.snp for _ in h5files]
        pool = Pool(self.bp_step)
        results = pool.map(is_snp_in_file, zip(snps, h5files))
        pool.close()
        pool.join()
        for h5file in results:
            if h5file is not None:
                return h5file

        # not found anywhere in chromosome
        raise NotFoundError("Chromosome-variant" + str(self.chromosome) + " " + self.snp)


def is_snp_in_file(tup):
    snp, h5file = tup
    searcher = service.Service(h5file)
    if searcher.snp_in_file(snp):
        return h5file
    return None
