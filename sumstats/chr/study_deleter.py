"""
    Data is stored in the hierarchy of /CHR/Study/DATA
    Deleter removes the Study group and therefore all the
    datasets within the study group.

"""
import os
from os.path import join
import glob
import pandas as pd

from collections import defaultdict
from sumstats.common_constants import *
from sumstats.errors.error_classes import *
import sumstats.utils.properties_handler as properties_handler
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class Deleter:

    def __init__(self, study, config_properties=None):
        self.study = study
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.chr_dir = self.properties.chr_dir
        assert study is not None, "You must specify a study to delete a study!"

    def delete_study(self):
        hdfs = glob.glob(os.path.join(self.search_path, self.chr_dir) + "/file_chr*.h5")
        for hdf in hdfs:
            with pd.HDFStore(hdf, mode='a') as store:
                self.delete_study_group_from_store(store)

    def delete_study_group_from_store(self, store):
        group = "/" + self.study
        if group in store.keys():
            store.remove('{}'.format(group))
        else:
            logger.debug("Study {} not found in {}!".format(self.study, store))
