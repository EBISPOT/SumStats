from sumstats.utils.query import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class StudyService:
    def __init__(self, h5file):
        # Open the file with read permissions
        self.datasets = {}
        self.pd_hdf = pd.HDFStore(h5file, mode='r')
        self.key = self.pd_hdf.keys()[0]
        self.study = get_study_metadata(hdf=self.pd_hdf, key=self.key)['study']
        self.chromosomes = get_study_metadata(hdf=self.pd_hdf, key=self.key)['chromosomes'].tolist()
        self.traits = get_study_metadata(hdf=self.pd_hdf, key=self.key)['traits'].tolist()


    def list_studies_for_trait(self, trait):
        trait_str = "molecular_trait_id == {}".format(trait)
        if len(self.pd_hdf.select(key=self.key, columns='molecular_trait_id', where=trait_str)) > 0:
            return self.study


    def list_traits_for_study(self, study_to_find):
        traits = []
        if self.study == study_to_find:
            """Store the below as a dataset in a group in the hdf5.
            Something, like /phen_info/[traits], we can keep an attribute linking to the trait metadata too.
            Same goes for genes"""
            #traits.extend(get_data(hdf=self.pd_hdf, key=self.key, fields=['molecular_trait_id'])['molecular_trait_id'].drop_duplicates().values.tolist())

            traits.extend(self.traits)
        return traits


    def has_trait(self, trait):
        trait_str = "molecular_trait_id == {}".format(trait)
        if any(self.pd_hdf.select(key=self.key, fields=['molecular_trait_id'], where=trait_str).drop_duplicates().values.tolist()):
            return True
        else:
            return False


    def close_file(self):
        logger.debug("Closing file %s...", self.study + '.h5')
        self.pd_hdf.close()
