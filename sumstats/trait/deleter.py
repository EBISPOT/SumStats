"""
    Data is stored in the hierarchy of /Trait/Study/DATA
    Deleter removes the Study group and therefore all the
    datasets within the study group.

"""

from sumstats.common_constants import *
from sumstats.errors.error_classes import *
import sumstats.utils.properties_handler as properties_handler
import sumstats.utils.filesystem_utils as fsutils
import sumstats.trait.search.access.study_service as study_service
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class Deleter:

    def __init__(self, study, config_properties=None):
        self.study = study
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.trait_dir = self.properties.trait_dir

        assert study is not None, "You must specify a study to delete a study!"

    def delete_study(self):
         hf_study = self._find_h5file_study_group()
         if hf_study is not None:
             for h5file, study in hf_study.items():
                 with h5py.File(h5file, 'r+') as hf:
                    del hf[study]


    def _find_h5file_study_group(self):
        """
        Traverse all the hdf5 file and find any with the study group of interest
        :return: dict of {h5file: studygroup path}
        """
        hf_study_dict = {}
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
        for h5file in h5files:
            service = study_service.StudyService(h5file=h5file)
            for study_group in service.get_study_groups():
                if self.study == study_group.get_name().split("/")[-1]:
                    hf_study_dict[h5file] = study_group.get_name()
            service.close_file()
        if any(hf_study_dict):
            return hf_study_dict
        else:
            logger.debug("Study %s not found in any trait!", self.study)
            raise NotFoundError("Study " + self.study)



