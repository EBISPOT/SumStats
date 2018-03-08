import os.path

import sumstats.trait.search.access.trait_service as service
import sumstats.utils.utils as utils
from sumstats.trait.constants import *
from sumstats.utils import search
from sumstats.errors.error_classes import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class TraitSearch:
    def __init__(self, trait, start, size, path=None):
        self.trait = trait
        self.start = start
        self.size = size
        if path is None:
            print("Retriever: setting default location for output files")
            path = "/output"
        self.path = path

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = 0

        self.h5file = utils.create_file_path(self.path, dir_name="bytrait", file_name=trait)
        if not os.path.isfile(self.h5file):
            raise NotFoundError("Trait " + trait)
        self.searcher = service.TraitService(self.h5file)
        self.max_size_of_trait = self.searcher.get_trait_size(self.trait)

    def search_trait(self, pval_interval=None):
        logger.info("Searching for trait %s", self.trait)
        method_arguments = {'trait': self.trait}
        restrictions = {'pval_interval': pval_interval}
        return search.general_search(search_obj=self, max_size=self.max_size_of_trait, arguments=method_arguments,
                                     restriction_dictionary=restrictions)

