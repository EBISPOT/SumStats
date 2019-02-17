"""
    Data is stored in the hierarchy of /Trait/Study/DATA
    Deleter removes the Study group and therefore all the
    datasets within the study group.

"""
import os

from sumstats.common_constants import *
from sumstats.errors.error_classes import *
import sumstats.explorer as ex
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
            for h5file, study_group in hf_study.items():
                trait = study_group.split("/")[1]
                with h5py.File(h5file, 'r+') as hf:
                    if self._trait_has_no_children_left(trait):
                        logger.info("Deleting {f}/{t}".format(f=h5file, t=trait))
                        del hf[trait]
                    else:
                        logger.info("Deleting {f}/{s}".format(f=h5file, s=study_group))
                        del hf[study_group]
        """
        Think about:
        1) deleting entire hdf5 for the trait if trait is deleted
        2) flushing out the free space - repack?
        3) keyboard input for confirming deletion.
        """

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

    def _trait_has_no_children_left(self, trait):
        explorer = ex.Explorer(config_properties=self.properties)
        studies = explorer.get_list_of_studies_for_trait(trait)
        if len(studies) == 1 and studies[0] == self.study:
            return True
        else:
            return False




