import os
import shutil

import sumstats.search as search
import tests.search.search_test_constants as search_arrays
import sumstats.trait.loader as loader
from tests.prep_tests import *
from sumstats.trait.constants import *
from tests.search.test_utils import *

class TestLoader(object):

    output_location = './output/bytrait/'
    file = None
    start = 0
    size = 20

    def setup_method(self, method):
        # output is always stored under a directory called: 'output'
        os.makedirs('./output/bytrait')

        # loaded s1/t1 -> 50 associations
        # loaded s2/t1 -> 50 associations
        # loaded s3/t2 -> 50 associations
        # loaded s4/t2 -> 50 associations
        # total associations loaded : 200

        search_arrays.chrarray = [1 for _ in range(50)]
        h5file = self.output_location + 'file_t1.h5'
        load = prepare_load_object_with_study_and_trait(h5file, 's1', 't1', loader, search_arrays)
        load.load()

        search_arrays.chrarray = [2 for _ in range(50)]
        load = prepare_load_object_with_study_and_trait(h5file, 's2', 't1', loader, search_arrays)
        load.load()

        h5file = self.output_location + 'file_t2.h5'
        search_arrays.chrarray = [1 for _ in range(50)]
        load = prepare_load_object_with_study_and_trait(h5file, 's3', 't2', loader, search_arrays)
        load.load()

        search_arrays.chrarray = [2 for _ in range(50)]
        load = prepare_load_object_with_study_and_trait(h5file, 's4', 't2', loader, search_arrays)
        load.load()

        # initialize searcher with local path
        self.searcher = search.Search(path="./output")

    def teardown_method(self, method):
        shutil.rmtree('./output')

    def test_search_t1_0_20(self):
        start = 0
        size = 20
        datasets, next_index = self.searcher.search_trait(trait='t1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_only_list_of_studies_returned(datasets, ['s1'])

    def test_search_t1_40_60(self):
        start = 40
        size = 20

        datasets, next_index = self.searcher.search_trait(trait='t1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_only_list_of_studies_returned(datasets, ['s1', 's2'])
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 10)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 10)

    def test_search_t1(self):
        start = 0
        size = 200

        datasets, next_index = self.searcher.search_trait(trait='t1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 100)
        assert_only_list_of_studies_returned(datasets, ['s1', 's2'])
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 50)

    def test_loop_through_t2_size_5(self):
        start = 0
        size = 5

        looped_through = 1

        while True:
            datasets, next_index = self.searcher.search_trait(trait='t2', start=start, size=size)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            if looped_through <= 10:
                assert_number_of_times_study_is_in_datasets(datasets, 's3', 5)
                assert_only_list_of_studies_returned(datasets, ['s3'])
            else:
                assert_number_of_times_study_is_in_datasets(datasets, 's4', 5)
                assert_only_list_of_studies_returned(datasets, ['s4'])
            looped_through += 1
            start = start + next_index

        assert looped_through == 21

    def test_loop_through_t2_size_42(self):
        start = 0
        size = 42

        looped_through = 1

        while True:
            datasets, next_index = self.searcher.search_trait(trait='t2', start=start, size=size)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            if looped_through <= 1:
                assert_number_of_times_study_is_in_datasets(datasets, 's3', 42)
                assert_only_list_of_studies_returned(datasets, ['s3'])
            elif looped_through == 2:
                assert_number_of_times_study_is_in_datasets(datasets, 's3', 8)
                assert_number_of_times_study_is_in_datasets(datasets, 's4', 34)
                assert_only_list_of_studies_returned(datasets, ['s3', 's4'])
            else:
                assert_number_of_times_study_is_in_datasets(datasets, 's4', 16)
                assert_only_list_of_studies_returned(datasets, ['s4'])
            looped_through += 1
            start = start + next_index
