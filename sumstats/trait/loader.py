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

"""

from sumstats.trait.constants import *
import sumstats.trait.constants as const
import sumstats.utils.fileload as fl
import sumstats.utils.group as gu
from sumstats.errors.error_classes import *


class Loader:

    def __init__(self, tsv, h5file, study, trait, dict_of_data=None):
        h5file = h5file
        self.study = study
        self.trait = trait

        assert trait is not None, "You need to specify a trait with the trait loader!"

        datasets_as_lists = fl.read_datasets_from_input(tsv, dict_of_data, const)
        self.datasets = fl.format_datasets(datasets_as_lists, study, const)

        # Open the file with read/write permissions and create if it doesn't exist
        self.file = h5py.File(h5file, 'a')
        self.file_group = gu.Group(self.file)

    def load(self):

        datasets = self.datasets

        trait_group = self._create_trait_group()
        study_group = self._create_study_group(trait_group)

        # group, dset_name, data
        for dset_name in TO_STORE_DSETS:
            study_group.generate_dataset(dset_name, datasets[dset_name])

    def _create_trait_group(self):
        self.file_group.create_subgroup(self.trait)
        return self.file_group.get_subgroup(self.trait)

    def _create_study_group(self, trait_group):
        if trait_group.subgroup_exists(self.study):
            self.close_file()
            raise AlreadyLoadedError(self.study)
        trait_group.create_subgroup(self.study)
        return trait_group.get_subgroup(self.study)

    def close_file(self):
        self.file.close()
