import os

import sumstats.trait.loader as loader
from sumstats.trait.search.trait_search import TraitSearch
from tests.prep_tests import *
import tests.test_constants as search_arrays
from config import properties
from sumstats.utils.interval import FloatInterval
import shutil

trait1 = "t1"
trait2 = "t2"
study1 = "s1"
study2 = "s2"
study3 = "s3"


class TestUnitTraitSearch(object):
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
        self.search = TraitSearch(trait=trait1, start=0, size=20, config_properties=properties)

    def teardown_method(self):
        shutil.rmtree('./output')

    def test_find_existing_trait_data(self):
        dataset, indexmarker = self.search.search_trait()
        assert indexmarker == 8
        assert len(dataset[REFERENCE_DSET]) == 8

    def test_find_existing_trait_data_with_pval_filter(self):
        pval_interval = FloatInterval().set_tuple(0.4, 0.5)
        dataset, indexmarker = self.search.search_trait(pval_interval=pval_interval)
        # note the difference in the index marker and the length of the returned dataset
        assert indexmarker == 8
        assert len(dataset[REFERENCE_DSET]) == 4
