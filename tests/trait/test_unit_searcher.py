import os

import pytest

import sumstats.trait.loader as loader
from sumstats.trait.searcher import Search
from tests.test_constants import *
from sumstats.trait.constants import TO_STORE_DSETS


class TestUnitSearcher(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        chrarray = [10, 10, 10, 10]

        loader_dictionary = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, "PM001", "Trait1", loader_dictionary)
        load.load()

        loader_dictionary = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, "PM002", "Trait1", loader_dictionary)
        load.load()

        loader_dictionary = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, "PM003", "Trait2", loader_dictionary)
        load.load()

        self.start = 0
        self.size = 20

        self.query = Search(self.h5file)

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_all_assocs(self):
        self.query.query_for_all_associations(self.start, self.size)
        datasets = self.query.get_result()
        study_set = set(datasets[STUDY_DSET])

        assert study_set.__len__() == 3

    def test_query_for_trait(self):
        self.query.query_for_trait("Trait1", self.start, self.size)
        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 8

        study_set = set(datasets[STUDY_DSET])

        assert study_set.__len__() == 2

        self.query.query_for_trait("Trait2", self.start, self.size)
        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

        study_set = set(datasets[STUDY_DSET])

        assert study_set.__len__() == 1

    def test_query_for_study(self):
        self.query.query_for_study("Trait1", "PM001", self.start, self.size)

        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

        study_set = set(datasets[STUDY_DSET])

        assert study_set.__len__() == 1
        assert "PM001" in study_set.pop()

        self.query.query_for_study("Trait1", "PM001", self.start, self.size)
        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

    def test_non_existing_trait(self):
        with pytest.raises(ValueError):
            self.query.query_for_trait("Trait3", self.start, self.size)

    def test_non_existing_trait_study_combination(self):
        with pytest.raises(ValueError):
            self.query.query_for_study("Trait3", "PM002", self.start, self.size)

