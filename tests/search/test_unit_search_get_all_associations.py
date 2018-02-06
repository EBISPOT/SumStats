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

    def test_size_start_0_size_50_returns_only_first_and_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=50)
        assert_only_list_of_studies_returned(datasets, ['s1'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)

    def test_size_51_returns_first_and_second_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=51)
        assert_only_list_of_studies_returned(datasets, ['s1', 's2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS,51)
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 1)

    def test_start_0_size_0(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=0)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)

    def test_start_50_size_50_returns_only_second_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=50, size=50)
        assert_only_list_of_studies_returned(datasets, ['s2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)

    def test_start_49_size_51_returns_first_and_second_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=49, size=51)
        assert_only_list_of_studies_returned(datasets, ['s1', 's2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 51)
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 1)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 50)

    def test_start_100_size_100_returns_third_and_fourth_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=100, size=100)
        assert_only_list_of_studies_returned(datasets, ['s3', 's4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 100)
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 50)

    def test_get_all(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=200)
        assert_only_list_of_studies_returned(datasets, ['s1', 's2', 's3', 's4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 200)
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 50)

    def test_get_all_size_bigger_than_existing_data(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=220)
        assert_only_list_of_studies_returned(datasets, ['s1', 's2', 's3', 's4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 200)
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 50)

    def test_get_all_loop_through_size_20(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
            start = start + size
            datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)

    def test_get_all_loop_through_0_to_20(self):
        start = 0
        size = 20
        # first 20 of study s1
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s1'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_all_loop_through_20_to_40(self):
        start = 20
        size = 20
        # 20-40 of study s1
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s1'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_all_loop_through_40_to_60(self):
        start = 40
        size = 20
        # 40-50 of study s1 and first 10 (remaining) of study s2
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s1', 's2'])
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 10)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 10)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_all_loop_through_60_to_80(self):
        start = 60
        size = 20
        # 10-30 of study s2
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_all_loop_through_80_to_100(self):
        start = 80
        size = 20
        # 30-50 of study s2
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_all_loop_through_100_to_120(self):
        start = 100
        size = 20
        # first 20 of study s3
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s3'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_all_loop_through_120_to_140(self):
        start = 120
        size = 20
        # 20 - 40 of study s3
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s3'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_all_loop_through_140_to_160(self):
        start = 140
        size = 20
        # 40 - 50 of study s3 and first 10 if study s4
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s3', 's4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 10)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 10)

    def test_get_all_loop_through_160_to_180(self):
        start = 160
        size = 20
        # 10 - 30 of study s4
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_all_loop_through_180_to_200(self):
        start = 180
        size = 20
        # 30 - 50 of study s4
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_only_list_of_studies_returned(datasets, ['s4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

    def test_get_out_of_bounds(self):
        start = 200
        size = 20
        # empty
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)
