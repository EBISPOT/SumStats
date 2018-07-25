import os.path

import sumstats.trait.search.access.study_service as service
import sumstats.utils.dataset_utils as utils
import sumstats.utils.filesystem_utils as fsutils
from sumstats.trait.constants import *
from sumstats.utils import search
from sumstats.errors.error_classes import *
import logging
from sumstats.utils import register_logger
from sumstats.utils import properties_handler

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class StudySearch:
    def __init__(self, trait, start, size, config_properties=None):
        self.trait = trait
        self.start = start
        self.size = size

        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.trait_dir = self.properties.trait_dir

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = 0

        self.h5file = fsutils.create_h5file_path(self.search_path, dir_name=self.trait_dir, file_name=trait)
        if not os.path.isfile(self.h5file):
            raise NotFoundError("Trait " + trait)
        self.searcher = service.StudyService(self.h5file)

    def search_study(self, study, pval_interval=None):
        """
        Search for the data of a study that lives under the StudySearch object's trait
        :param study: name of the study we are searching for (str)
        :param pval_interval: optional p-value interval of type FloatInterval
        :return: a tuple (datasets, index_marker) where 'datasets' is a dictionary with the names of the datasets and
        the data to be returned (the result of the query after applying restrictions) and index_marker is an integer indicating
        up to where the query went in the dataset so that the next query can calculate it's next start base on the index_marker.
        """
        logger.info("Searching for study %s with pval_interval %s", study, str(pval_interval))
        method_arguments = {'trait': self.trait, 'study': study}
        total_study_size = self.searcher.get_study_size(self.trait, study)
        restrictions = {'pval_interval': pval_interval}
        return search.general_search(search_obj=self, max_size=total_study_size, arguments=method_arguments,
                                     restriction_dictionary=restrictions)
