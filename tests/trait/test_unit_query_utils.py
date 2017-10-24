import os
import pytest
import sumstats.trait.loader as loader
import sumstats.trait.query_utils as query
from tests.trait.test_constants import *
from sumstats.trait.constants import *


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        chrarray = [10, 10, 10, 10]

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, "PM001", "Trait1", dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, "PM002", "Trait1", dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, "PM003", "Trait2", dict)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode='a')

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_dsets_from_file(self):
        name_to_dataset = query.get_dsets_from_file(self.f)

        assert len(set(name_to_dataset[STUDY_DSET])) == 3
        for dset_name in TO_QUERY_DSETS:
            assert len(name_to_dataset[dset_name]) == 12

    def test_get_dsets_from_trait_group(self):
        trait_group = self.f.get("Trait2")
        name_to_dsets = query.get_dsets_from_trait_group(trait_group)

        assert len(set(name_to_dsets[STUDY_DSET])) == 1
        for dset_name in TO_QUERY_DSETS:
            assert len(name_to_dsets[dset_name]) == 4

        trait_group = self.f.get("Trait1")
        name_to_dsets = query.get_dsets_from_trait_group(trait_group)

        assert len(set(name_to_dsets[STUDY_DSET])) == 2
        for dset_name in TO_QUERY_DSETS:
            assert len(name_to_dsets[dset_name]) == 8

    def test_get_dsets_from_group(self):
        study_group = self.f.get("Trait2/PM003")
        name_to_dsets = query.get_dsets_from_group("PM003", study_group)

        assert len(set(name_to_dsets[STUDY_DSET])) == 1
        for dset_name in TO_QUERY_DSETS:
            assert len(name_to_dsets[dset_name]) == 4