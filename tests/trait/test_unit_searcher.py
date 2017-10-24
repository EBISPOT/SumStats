import os
import pytest
import sumstats.trait.loader as loader
from sumstats.trait.searcher import Search
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

        self.query = Search(self.h5file)

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_trait(self):
        name_to_dataset = self.query.query_for_trait("Trait1")
        for dset_name in TO_STORE_DSETS:
            assert len(name_to_dataset[dset_name]) == 8

        study_set = set(name_to_dataset[STUDY_DSET])

        assert study_set.__len__() == 2

        name_to_dataset = self.query.query_for_trait("Trait2")
        for dset_name in TO_STORE_DSETS:
            assert len(name_to_dataset[dset_name]) == 4

        study_set = set(name_to_dataset[STUDY_DSET])

        assert study_set.__len__() == 1

    def test_query_for_study(self):
        name_to_dataset = self.query.query_for_study("Trait1", "PM001")

        for dset_name in TO_STORE_DSETS:
            assert len(name_to_dataset[dset_name]) == 4

        study_set = set(name_to_dataset[STUDY_DSET])

        assert study_set.__len__() == 1
        assert "PM001" in study_set.pop()

        name_to_dataset = self.query.query_for_study("Trait1", "PM001")
        for dset_name in TO_STORE_DSETS:
            assert len(name_to_dataset[dset_name]) == 4

    def test_non_existing_trait(self):
        with pytest.raises(ValueError):
            self.query.query_for_trait("Trait3")

    def test_non_existing_trait_study_combination(self):
        with pytest.raises(ValueError):
            self.query.query_for_study("Trait3", "PM002")

