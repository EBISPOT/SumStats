"""
    Data is stored in the hierarchy of /Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    'snp' list will hold the snp ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'chr' list will hold the chromosome that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    snp[0], mantissa[0], exp[0], and chr[0] hold the information for SNP 0

    Query : Retrieve all the information for a study: input = and study name and trait name
"""

import sumstats.trait.search.access.repository as repo
import sumstats.utils.group as gu
from sumstats.utils.query import *
import sumstats.utils.restrictions as rst
from sumstats.common_constants import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class StudyService:
    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}
        self.file_group = gu.Group(self.file)
        self.pd_hdf = pd.HDFStore(h5file)
        self.key = self.file_group.get_all_subgroups_keys()[0]
        self.study = get_study_metadata(hdf=self.pd_hdf, key=self.key)['study']
        self.tissue = get_study_metadata(hdf=self.pd_hdf, key=self.key)['tissue']


    def list_studies_for_trait(self, trait):
        trait_str = "molecular_trait_id == {}".format(trait)
        if len(self.pd_hdf.select(key=self.key, columns='molecular_trait_id', where=trait_str)) > 0:
            return self.study


    def list_traits_for_study(self, study_to_find):
        traits = []
        if self.study == study_to_find:
            traits.extend(get_data(hdf=self.pd_hdf, key=self.key, fields=['molecular_trait_id'])['molecular_trait_id'].drop_duplicates().values.tolist())
        return traits



    def list_tissue_study_pairs(self):
        tissue_study_pairs = []
        for (study, subgroups, tissues) in self.pd_hdf.walk():
            for tissue in tissues:
                key = '/'.join([study, tissue])
                tissue_study_pairs.append(key)
        return tissue_study_pairs

    def has_trait(self, trait):
        trait_str = "molecular_trait_id == {}".format(trait)
        if any(self.pd_hdf.select(key=self.key, fields=['molecular_trait_id'], where=trait_str).drop_duplicates().values.tolist()):
            return True
        else:
            return False




#    def list_trait_study_pairs(self):
#        trait_groups = self.file_group.get_all_subgroups()
#        study_groups = []
#
#        for trait_group in trait_groups:
#            trait_group_name = trait_group.get_name().replace("/","")
#            study_groups.extend([trait_group_name + ":" + study_name for study_name in trait_group.get_all_subgroups_keys()])
#        return study_groups
#
#    def get_study_groups(self):
#        trait_groups = self.file_group.get_all_subgroups()
#        study_groups = gu.generate_subgroups_from_generator_of_subgroups(trait_groups)
#        return study_groups

    def close_file(self):
        logger.debug("Closing file %s...", self.file.file)
        self.file.close()
        self.pd_hdf.close()
