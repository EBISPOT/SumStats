import os

import pytest

import sumstats.trait.loader as loader
from sumstats.utils.interval import FloatInterval
from sumstats.trait.search.study_search import StudySearch
from tests.prep_tests import *
import tests.test_constants as search_arrays
from config import properties
from sumstats.errors.error_classes import *
import shutil

trait1 = "t1"
trait2 = "t2"
study1 = "s1"
study2 = "s2"
study3 = "s3"


class TestUnitStudySearch(object):
    output_location = './output/bytrait/'

    h5file1 = output_location + 'file_t1.h5'
    h5file2 = output_location + 'file_t2.h5'

    def setup_method(self):
        os.makedirs('./output/bytrait')
        search_arrays.chrarray = [10, 10, 10, 10]

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study=study1, loader=loader, trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study=study2, loader=loader, trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file2, study=study3, loader=loader, trait=trait2,
                                                        test_arrays=search_arrays)
        load.load()

        self.start = 0
        self.size = 20
        properties.h5files_path = "./output"
        self.search = StudySearch(trait=trait1, start=0, size=20, config_properties=properties)

    def teardown_method(self):
        shutil.rmtree('./output')

    def test_find_existing_study_data(self):
        dataset, indexmarker = self.search.search_study(study=study1)
        assert indexmarker == 4
        assert len(dataset[REFERENCE_DSET]) == 4

    def test_find_existing_study_data_with_pval_filter(self):
        pval_interval = FloatInterval().set_tuple(0.4, 0.5)
        dataset, indexmarker = self.search.search_study(study=study1, pval_interval=pval_interval)
        # This shows that the index marker traversed the whole dataset that is of size 4, but
        # but only returned 2 data elements because the other 2 where filtered out due to the pval filter
        # but still the index marker is 4 because we traversed all 4 elements of the dataset
        assert indexmarker == 4
        assert len(dataset[REFERENCE_DSET]) == 2

    def test_find_non_existing_study_raises_error(self):
        with pytest.raises(SubgroupError):
            self.search.search_study(study=study3)
