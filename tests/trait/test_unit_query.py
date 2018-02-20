import os

import pytest

import sumstats.trait.loader as loader
import sumstats.trait.search.access.repository as query
from sumstats.trait.constants import *
from tests.prep_tests import *
import tests.test_constants as search_arrays

trait1 = "t1"
trait2 = "t2"
trait3 = "t3"
study1 = "s1"
study2 = "s2"
study3 = "s3"


class TestUnitQueryUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self):

        search_arrays.chrarray = [10, 10, 10, 10]
        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study1, loader=loader, trait=trait1, test_arrays=search_arrays)

        load.load()

        search_arrays.chrarray = [10, 10, 10, 10]
        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study2, loader=loader,
                                                        trait=trait1, test_arrays=search_arrays)
        load.load()

        search_arrays.chrarray = [10, 10, 10, 10]
        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study3, loader=loader,
                                                        trait=trait2, test_arrays=search_arrays)

        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode='a')
        self.start = 0
        self.size = 20
        self.file_group = gu.Group(self.f)

    def teardown_method(self):
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
        trait_group = self.file_group.get_subgroup(trait2)

        datasets = query.get_dsets_from_trait_group(trait_group, self.start, self.size)

        assert len(set(datasets[STUDY_DSET])) == 1
        for dset_name in TO_QUERY_DSETS:
            assert len(datasets[dset_name]) == 4

        trait_group = self.file_group.get_subgroup(trait1)
        datasets = query.get_dsets_from_trait_group(trait_group, self.start, self.size)

        assert len(set(datasets[STUDY_DSET])) == 2
        for dset_name in TO_QUERY_DSETS:
            assert len(datasets[dset_name]) == 8

    def test_get_dsets_from_group(self):
        study_group = self.file_group.get_subgroup(trait2 + "/" + study3)
        datasets = query.get_dsets_from_group_directly(study3, study_group, self.start, self.size)

        assert len(set(datasets[STUDY_DSET])) == 1
        for dset_name in TO_QUERY_DSETS:
            assert len(datasets[dset_name]) == 4