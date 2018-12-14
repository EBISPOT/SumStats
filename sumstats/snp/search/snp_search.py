"""
    Stored as /SNP/DATA
    Where DATA:
    under each directory we store 3 (or more) vectors
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'bp' list will hold the baise pair location that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    for a SNP group:
    study[0], mantissa[0], exp[0], and bp[0] hold the information for this SNP for study[0]

"""
import sumstats.snp.search.access.service as snp_service
from sumstats.chr.search.access import block_service
import sumstats.utils.dataset_utils as utils
import sumstats.utils.filesystem_utils as fsutils
from sumstats.snp.constants import *
from sumstats.utils import search
from sumstats.utils.interval import *
from sumstats.errors.error_classes import *
import logging
from sumstats.utils import register_logger
from multiprocessing import Pool
from sumstats.utils import properties_handler
from sumstats.utils.ensembl_rest_client import EnsemblRestClient
import sumstats.chr.search.block_search as bs
import sumstats.chr.retriever as cr
import os
import re

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class SNPSearch:
    """
    When a SNPSearch object is initiated it can have a chromosome passed via it's constructor or not.
    SNPSearch needs to initiate the Service object and that in turn needs the hdf5 file that the snp we are searching
    for belongs to. In order to do this it needs the chromosome information.
    If the chromosome information is given, we just need to check the the directory for that chromosome exists and that
    find the exact file that that snp lives in (under the chromosome directory).
    If the chromosome is not given, we need to search for the snp and it's exact file (the same as we would do if we
    knew the chromosome) but we need to do this in all the chromosomes until we find it or run out of chromosomes.
    """
    def __init__(self, snp, start, size, config_properties=None, chromosome=None):
        self.snp = snp
        self.start = start
        self.size = size
        self.chromosome = chromosome

        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)

        self.chr_dir = self.properties.chr_dir
        self.snp_dir = self.properties.snp_dir
        self.bp_step = self.properties.bp_step

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        self.index_marker = 0

        #if chromosome is None:
        #    self.service = self._calculate_snp_service()
        #else:
        #    self.service = self._get_snp_service()
        self.chromosome, self.bp_interval = self._parse_chromosome_bp_location()
        #self.h5file = fsutils.create_h5file_path(path=self.search_path, dir_name=self.chr_dir, file_name=self.chromosome)
        #if not os.path.isfile(self.h5file):
        #    raise NotFoundError("Chromosome " + str(self.chromosome))
        #self.service = block_service.BlockService(self.h5file)

    #def search_snp(self, study=None, pval_interval=None):
    #    logger.info("Searching for variant %s", self.snp)
    #    max_size = self.service.get_snp_size(self.snp)
    #    method_arguments = {'snp': self.snp}
    #    restrictions = {'pval_interval': pval_interval, 'study': study}
    #    return search.general_search(search_obj=self, max_size=max_size,
    #                                 arguments=method_arguments, restriction_dictionary=restrictions)

    """
    Search the chromosome implementation based on bp position
    """


    def search_snp(self, study=None, pval_interval=None):
        return cr.search_chromosome(chromosome=self.chromosome, start=self.start, size=self.size,
                                        properties=self.properties,
                                        bp_interval=self.bp_interval, study=study, pval_interval=pval_interval, snp=self.snp)

    def _get_bp_from_ensembl(self):
        client = EnsemblRestClient()
        return client.resolve_location_with_rest(self.snp)


    def _parse_chromosome_bp_location(self):
        bp_interval = self._get_bp_from_ensembl()
        print(bp_interval)
        if re.match(r'[0-9XYMT]{2}:[0-9]+-[0-9]+', bp_interval):
            chromosome, bp = bp_interval.split(':')
            bp_lower = str(int(bp.split('-')[0]) - 10000)
            bp_upper = str(int(bp.split('-')[0]) + 10000)
            bp_interval = ':'.join([bp_lower, bp_upper])
            bp_interval = IntInterval().set_string_tuple(bp_interval)
            return chromosome, bp_interval
        # Need to handle this not working




    def _calculate_snp_service(self):
        """
        Traverses all the chromosomes and tries to find the SNP in one of them.
        :return: Returns the Service object for the SNP or raises an error if not found
        """
        logger.debug("Calculating chromosome for variant %s...", self.snp)

        for chromosome in range(1, (self.properties.available_chromosomes + 1)):
            self.service = self._calculate_snp_service_for_chromosome(chromosome)
            if self.service is not None:
                return self.service
        # if not returned yet, not found
        logger.debug("Variant %s not found in any chromosome!", self.snp)
        raise NotFoundError("Variant " + self.snp)

    def _calculate_snp_service_for_chromosome(self, chromosome):
        """
        For the given chromosome see if the SNP given exists in one of it's files
        :param chromosome: the chromosome we think the SNP is in
        :return: the service created for this SNP to be searched
        """
        try:
            h5file = self._location_for_snp_in_chromosome(chromosome)
        except NotFoundError:
            return None
        logger.debug("Variant %s found in chromosome %s", self.snp, str(chromosome))
        return snp_service.Service(h5file)

    def _get_snp_service(self):
        h5file = self._location_for_snp_in_chromosome(self.chromosome)
        return snp_service.Service(h5file)

    def _location_for_snp_in_chromosome(self, chromosome):
        """
        Looks up all the files under the chromosome directory, in parallel, and tries to find out which one the
        SNP lives in.
        :param chromosome: the chromosome we think the SNP lives in
        :return: the exact file that this SNP is stored in or raises and error if not found
        """
        dir_name = fsutils.join(self.snp_dir, str(chromosome))
        if not fsutils.is_valid_dir_path(path=self.search_path, dir_name=dir_name):
            logger.debug(
                "Chromosome %s given for variant %s doesn't exist!", str(self.chromosome), self.snp)
            raise NotFoundError("Chromosome " + str(self.chromosome))
        h5files = fsutils.get_h5files_in_dir(path=self.search_path, dir_name=dir_name)

        snps = [self.snp for _ in h5files]
        pool = Pool(self.bp_step)
        results = pool.map(is_snp_in_file, zip(snps, h5files))
        pool.close()
        pool.join()
        for h5file in results:
            if h5file is not None:
                return h5file

        # not found anywhere in chromosome
        raise NotFoundError("Chromosome-variant combination")


def is_snp_in_file(tup):
    snp, h5file = tup
    service = snp_service.Service(h5file)
    if service.snp_in_file(snp):
        return h5file
    return None
