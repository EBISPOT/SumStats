import sumstats.search as search
import sumstats.utils.utils as utils
from sumstats.trait.constants import *
from tests.search.test_utils import *
from sumstats.errors.error_classes import *
import pytest


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self):
        # initialize searcher with local path
        self.searcher = search.Search(path="./outputtrait")

    def test_search_raises_error(self):
        with pytest.raises(NotFoundError):
            self.searcher.search_trait(trait='t5', start=0, size=20)

    def test_search_t1_0_20(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search_trait(trait='t1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1'])
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_search_t1_40_60(self):
        start = 40
        size = 20

        datasets, index_marker = self.searcher.search_trait(trait='t1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1', 's2'])
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 10)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 10)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_search_t1(self):
        start = 0
        size = 200

        datasets, index_marker = self.searcher.search_trait(trait='t1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 100)
        assert_studies_from_list(datasets, ['s1', 's2'])
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 50)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_loop_through_t2_size_5(self):
        start = 0
        size = 5

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

        while True:
            datasets, index_marker = self.searcher.search_trait(trait='t2', start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            if looped_through <= 10:
                assert_number_of_times_study_is_in_datasets(datasets, 's3', 5)
                assert_studies_from_list(datasets, ['s3'])
            else:
                assert_number_of_times_study_is_in_datasets(datasets, 's4', 5)
                assert_studies_from_list(datasets, ['s4'])
            looped_through += 1
            start = start + index_marker

        assert looped_through == 21
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])

    def test_loop_through_t2_size_42(self):
        start = 0
        size = 42

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

        while True:
            datasets, index_marker = self.searcher.search_trait(trait='t2', start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            if looped_through <= 1:
                assert_number_of_times_study_is_in_datasets(datasets, 's3', 42)
                assert_studies_from_list(datasets, ['s3'])
            elif looped_through == 2:
                assert_number_of_times_study_is_in_datasets(datasets, 's3', 8)
                assert_number_of_times_study_is_in_datasets(datasets, 's4', 34)
                assert_studies_from_list(datasets, ['s3', 's4'])
            else:
                assert_number_of_times_study_is_in_datasets(datasets, 's4', 16)
                assert_studies_from_list(datasets, ['s4'])
            looped_through += 1
            start = start + index_marker

        assert looped_through == 4
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])