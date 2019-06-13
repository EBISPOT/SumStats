import os
from os.path import join
import glob
import itertools

from sumstats.common_constants import *
from sumstats.errors.error_classes import *
import sumstats.utils.properties_handler as properties_handler
import sumstats.utils.sqlite_client as sq
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class Deleter:

    def __init__(self, study, config_properties=None):
        self.study = study
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.study_dir = self.properties.study_dir
        self.database = self.properties.sqlite_path
        
        assert study is not None, "You must specify a study to delete a study!"

   
    def delete_study_hdfs(self):
        hdfs = self.get_hdfs_for_study()
        if hdfs:
            for hdf in hdfs:
                logger.info("Deleting file: {}".format(hdf))
                os.remove(hdf)


    def get_hdfs_for_study(self):
        sql = sq.sqlClient(self.database)
        file_ids = []
        if sql.get_file_id_for_study(self.study):
            file_ids.extend(sql.get_file_id_for_study(self.study))
            hdfs = [glob.glob(os.path.join(self.search_path, self.study_dir) + "/*/file_" + f + ".h5") for f in file_ids]
            return list(itertools.chain.from_iterable(hdfs))
        else:
            logger.debug("No study files to delete associated with study: {}".format(self.study))
            return None
