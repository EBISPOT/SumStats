import os

import pytest

import sumstats.trait.loader as loader
import sumstats.trait.search.access.repository as query
import sumstats.utils.group as gu
from sumstats.trait.constants import *
from tests.test_constants import *


class TestUnitQueryUtils(object):
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

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode='a')
        self.start = 0
        self.size = 20
        self.file_group = gu.Group(self.f)

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_dsets_from_file_group_raises_error_when_file_given(self):
        with pytest.raises(KeyError):
            query.get_dsets_from_file_group(self.f, self.start, self.size)

    def test_get_dsets_from_file_group(self):
        datasets = query.get_dsets_from_file_group(self.file_group, self.start, self.size)
        assert len(set(datasets[STUDY_DSET])) == 3
        for dset_name in TO_QUERY_DSETS:
            assert len(datasets[dset_name]) == 12

    def test_get_dsets_from_trait_group(self):
        trait_group = self.file_group.get_subgroup("Trait2")

        datasets = query.get_dsets_from_trait_group(trait_group, self.start, self.size)

        assert len(set(datasets[STUDY_DSET])) == 1
        for dset_name in TO_QUERY_DSETS:
            assert len(datasets[dset_name]) == 4

        trait_group = self.file_group.get_subgroup("Trait1")
        datasets = query.get_dsets_from_trait_group(trait_group, self.start, self.size)

        assert len(set(datasets[STUDY_DSET])) == 2
        for dset_name in TO_QUERY_DSETS:
            assert len(datasets[dset_name]) == 8

    def test_get_dsets_from_group(self):
        study_group = self.file_group.get_subgroup("Trait2/PM003")
        datasets = query.get_dsets_from_group_directly("PM003", study_group, self.start, self.size)

        assert len(set(datasets[STUDY_DSET])) == 1
        for dset_name in TO_QUERY_DSETS:
            assert len(datasets[dset_name]) == 4