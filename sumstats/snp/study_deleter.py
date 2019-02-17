"""
    Data is stored in the hierarchy of /SNP/Study/DATA
    Deleter removes the Study group and therefore all the
    datasets within the study group.

"""
import os
from os.path import join
from glob import glob

from collections import defaultdict
from sumstats.common_constants import *
from sumstats.errors.error_classes import *
import sumstats.utils.properties_handler as properties_handler
import sumstats.utils.group as gu
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class Deleter:

    def __init__(self, study, config_properties=None):
        self.study = study
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.snp_dir = self.properties.snp_dir

        assert study is not None, "You must specify a study to delete a study!"

    def delete_study(self):
        hf_study = self._find_h5file_study_group()
        if hf_study is not None:
            for h5file, study_group_list in hf_study.items():
                with h5py.File(h5file, 'r+') as hf:
                    for sg in study_group_list:
                        logger.info("Deleting {f}/{s}".format(f=h5file, s=sg))
                        del hf[sg]


    def _find_h5file_study_group(self):
        """
        Traverse all the hdf5 file and find any with the study group of interest
        :return: dict of {h5file: studygroup path}
        """
        hf_study_dict = defaultdict(list)
        snp_path = join(self.search_path, self.snp_dir)
        h5files = [y for x in os.walk(snp_path) for y in glob(os.path.join(x[0], '*.h5'))]

        for h5file in h5files:

            hf_study_dict.update(self._get_dict_of_h5_to_study_groups(h5file, hf_study_dict))
        if any(hf_study_dict):
            return hf_study_dict
        else:
            logger.debug("Study %s not found in any variant!", self.study)
            raise NotFoundError("Study " + self.study)

    def _get_dict_of_h5_to_study_groups(self, h5file, hf_study_dict):
        file = h5py.File(h5file, 'r')
        file_group = gu.Group(file)
        snp_groups = file_group.get_all_subgroups()
        study_groups = gu.generate_subgroups_from_generator_of_subgroups(snp_groups)
        for study_group in study_groups:
            if self.study == study_group.get_name().split("/")[-1]:
                snp_group = study_group.get_parent()
                if len(snp_group.get_all_subgroups_keys()) == 1:
                    hf_study_dict[h5file].append(snp_group.get_name())
                else:
                    hf_study_dict[h5file].append(study_group.get_name())
        file.close()
        return hf_study_dict
