"""
    Stored as /CHR/BLOCK/DATA
    Where DATA:
    under each BLOCK directory we store 3 (or more) vectors
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    for a SNP group:
    study[0], mantissa[0], exp[0], and bp[0] hold the information for this SNP for study[0]
"""

import os.path

from sumstats.chr.search.access import chromosome_service
import sumstats.utils.utils as utils
from sumstats.chr.constants import *
from sumstats.utils import search
from sumstats.errors.error_classes import *
import logging
from sumstats.utils import register_logger
from sumstats.utils import properties_handler

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class ChromosomeSearch:
    def __init__(self, chromosome, start, size, config_properties=None):
        self.chromosome = chromosome
        self.start = start
        self.size = size

        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.chr_dir = self.properties.chr_dir

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        self.index_marker = 0

        self.h5file = utils.create_h5file_path(path=self.search_path, dir_name=self.chr_dir, file_name=chromosome)

        if not os.path.isfile(self.h5file):
            raise NotFoundError("Chromosome " + str(chromosome))
        self.service = chromosome_service.ChromosomeService(self.h5file)

    def search_chromosome(self, study=None, pval_interval=None):
        logger.info("Searching for chromosome %s", str(self.chromosome))
        max_size = self.service.get_chromosome_size(chromosome=self.chromosome)
        method_arguments = {'chromosome': self.chromosome}
        restrictions = {'pval_interval': pval_interval, 'study': study}
        return search.general_search(search_obj=self, max_size=max_size,
                                     arguments=method_arguments, restriction_dictionary=restrictions)
