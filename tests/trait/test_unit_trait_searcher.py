import os

import pytest

import sumstats.trait.loader as loader
from sumstats.trait.constants import TO_STORE_DSETS
from sumstats.trait.search.access.trait_service import TraitService
from tests.prep_tests import *
import tests.test_constants as search_arrays
from sumstats.errors.error_classes import *

trait1 = "t1"
trait2 = "t2"
trait3 = "t3"
study1 = "s1"
study2 = "s2"
study3 = "s3"


class TestUnitSearcher(object):
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

        self.query = TraitService(self.h5file)

    def teardown_method(self):
        os.remove(self.h5file)

    def test_query_for_trait(self):
        self.query.query(trait1, self.start, self.size)
        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 8

        study_set = set(datasets[STUDY_DSET])

        assert len(study_set) == 2

        self.query.query(trait2, self.start, self.size)
        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

        study_set = set(datasets[STUDY_DSET])

        assert len(study_set) == 1

    def test_non_existing_trait(self):
        with pytest.raises(NotFoundError):
            self.query.query(trait3, self.start, self.size)

