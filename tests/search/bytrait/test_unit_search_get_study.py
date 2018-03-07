
import sumstats.controller as search
from sumstats.trait.constants import *
from tests.search.test_utils import *


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self, method):
        # initialize searcher with local path
        self.searcher = search.Search(path="./outputtrait")

    def test_search_s1_0_20(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1'])

    def test_search_s1_0_200(self):
        start = 0
        size = 200
        datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)
        assert_studies_from_list(datasets, ['s1'])

    def test_search_s1_40_60(self):
        start = 40
        size = 20

        datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 10)
        assert_studies_from_list(datasets, ['s1'])

    def test_search_s2_40_60(self):
        start = 40
        size = 20

        datasets, index_marker = self.searcher.search_study(trait='t1', study='s2', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 10)
        assert_studies_from_list(datasets, ['s2'])

    def test_loop_through_s3_size_5(self):
        start = 0
        size = 5

        looped_through = 1

        while True:
            datasets, index_marker = self.searcher.search_study(trait='t2', study='s3', start=start, size=size)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            assert_number_of_times_study_is_in_datasets(datasets, 's3', 5)
            assert_studies_from_list(datasets, ['s3'])
            looped_through += 1
            start = start + index_marker

        assert looped_through == 11

    def test_loop_through_s3_size_42(self):
        start = 0
        size = 42

        looped_through = 1

        while True:
            datasets, index_marker = self.searcher.search_study(trait='t2', study='s3', start=start, size=size)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            if looped_through <= 1:
                assert_number_of_times_study_is_in_datasets(datasets, 's3', 42)
                assert_studies_from_list(datasets, ['s3'])
            else:
                assert_number_of_times_study_is_in_datasets(datasets, 's3', 8)
                assert_studies_from_list(datasets, ['s3'])
            looped_through += 1
            start = start + index_marker

        assert looped_through == 3
