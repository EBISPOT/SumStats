"""
    Data is stored in the hierarchy of /Trait/Study/DATA
    Deleter removes the Study group and therefore all the
    datasets within the study group.

"""

from sumstats.common_constants import *
import sumstats.utils.group as gu
from sumstats.errors.error_classes import *
import sumstats.explorer as ex
import sumstats.utils.properties_handler as properties_handler
import sumstats.utils.filesystem_utils as fsutils
import sumstats.trait.search.access.study_service as study_service


class Deleter:

    def __init__(self, study, config_properties=None):
        self.study = study
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.trait_dir = self.properties.trait_dir

        assert study is not None, "You must specify a study to delete a study!"


    def delete_study(self):
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
        for h5file in h5files:
            print(h5file)
            service = study_service.StudyService(h5file=h5file)
            for study_group in service.get_study_groups():
                if self.study == study_group.get_name().split("/")[-1]:

                    with h5py.File(h5file, 'r+') as hf:
                        del hf[study_group.get_name()]

                #    return hf[study_group.get_name()]


#    def find_study_group(self):
#        h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
#        for h5file in h5files:
#            service = study_service.StudyService(h5file=h5file)
#            for study_group in service.get_study_groups():
#                if self.study == study_group.get_name().split("/")[-1]:
#                    service.close_file()
#                    #with h5py.File(h5file, 'a') as hf:
#                    if isinstance(h5file, h5py.File):
#                        print(h5file.name())
#                    return h5file, study_group
#            service.close_file()
#        raise NotFoundError("Study " + self.study)
