import os

import pytest

import sumstats.trait.loader as loader
from sumstats.trait.constants import TO_STORE_DSETS
from sumstats.trait.search.access.trait_service import TraitService
from tests.prep_tests import *
import tests.test_constants as search_arrays
from sumstats.errors.error_classes import *
from sumstats.utils.interval import FloatInterval

trait1 = "t1"
trait2 = "t2"
trait3 = "t3"
study1 = "s1"
study2 = "s2"
study3 = "s3"


class TestUnitTraitService(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self):
        search_arrays.chrarray = [10, 10, 10, 10]

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study1, loader=loader, trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study2, loader=loader, trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study3, loader=loader, trait=trait2,
                                                        test_arrays=search_arrays)
        load.load()

        self.start = 0
        self.size = 20

        self.service = TraitService(self.h5file)

    def teardown_method(self):
        os.remove(self.h5file)

    def test_query_for_trait_1(self):
        self.service.query(trait1, self.start, self.size)
        datasets = self.service.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 8

        study_set = set(datasets[STUDY_DSET])

        assert len(study_set) == 2

        self.service.query(trait2, self.start, self.size)
        datasets = self.service.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

        study_set = set(datasets[STUDY_DSET])

        assert len(study_set) == 1

    def test_query_for_trait_2(self):
        self.service.query(trait2, self.start, self.size)
        datasets = self.service.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

        study_set = set(datasets[STUDY_DSET])

        assert len(study_set) == 1

    def test_query_for_trait_1_with_pval_restrictions(self):
        self.service.query(trait1, self.start, self.size)

        # pvalsarray = ["0.4865", "0.4314", "0.5986", "0.07057"]
        pval_interval = FloatInterval().set_tuple(None, 0.49)
        self.service.apply_restrictions(pval_interval=pval_interval)

        datasets = self.service.get_result()
        # 3 results times 2 studies loaded
        assert len(datasets[REFERENCE_DSET]) == 6

        study_set = set(datasets[STUDY_DSET])

        assert len(study_set) == 2

    def test_get_trait_1_size(self):
        trait_size = self.service.get_trait_size(trait1)
        # trait 1 has 2 studies
        # each study has size 4
        assert trait_size == 8

    def test_get_trait_2_size(self):
        trait_size = self.service.get_trait_size(trait2)
        # trait 2 has 1 study
        # each study has size 4
        assert trait_size == 4

    def test_list_traits(self):
        # lists the traits of the file that was given
        list_of_traits = self.service.list_traits()
        assert len(list_of_traits) == 2

    def test_t1_exists(self):
        assert self.service.has_trait(trait1)

    def test_t2_exists(self):
        assert self.service.has_trait(trait2)

    def test_trait_doesnt_exist(self):
        assert not self.service.has_trait(trait3)

    def test_non_existing_trait(self):
        with pytest.raises(NotFoundError):
            self.service.query(trait3, self.start, self.size)

