import sumstats.controller as search
from sumstats.trait.constants import *
from tests.search.test_utils import *
from sumstats.utils.interval import *
from config import properties


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self, method):
        # initialize searcher with local path
        properties.h5files_path = "./outputtrait"
        self.searcher = search.Search(properties)

    def test_search_s1_0_20_lower_pval(self):
        start = 0
        size = 20
        pval_interval = FloatInterval().set_tuple(0.00001, 0.00005)
        datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1'])

        assert index_marker == 20

    def test_search_s1_0_20_upper_pval(self):
        start = 0
        size = 20
        pval_interval = FloatInterval().set_tuple(0.00005, 0.01)
        datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size,
                                                          pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1'])

        assert index_marker == 45

    def test_search_s1_0_50_lower_pval(self):
        start = 0
        size = 50
        pval_interval = FloatInterval().set_tuple(0.00001, 0.00005)
        datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size,
                                                          pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 25)
        assert_studies_from_list(datasets, ['s1'])

        assert index_marker == 50

    def test_search_s1_0_50_upepr_pval(self):
        start = 0
        size = 50
        pval_interval = FloatInterval().set_tuple(0.00005, 0.01)
        datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size,
                                                          pval_interval=pval_interval)
        assert_studies_from_list(datasets, ['s1'])
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 25)

        assert index_marker == 50

    def test_search_t2_45_65(self):
        start = 45
        size = 20

        pval_interval = FloatInterval().set_tuple(0.006, 0.1)
        datasets, index_marker = self.searcher.search_study(trait='t2', study='s3', start=start, size=size,
                                                          pval_interval=pval_interval)
        assert_studies_from_list(datasets, ['s3'])
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 5)

        # retrived 5 in total so start + index_marker = 50 -> where we will query next (if there where more elements
        # for this study)
        # this is the end of this trait so it comes down to 5 instead of 20
        assert index_marker == 5

    def test_loop_through_s1_size_5(self):
        start = 0
        size = 5
        # second half of s1
        pval_interval = FloatInterval().set_tuple(0.0001, 0.1)

        looped_through = 1

        while True:
            datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size, pval_interval=pval_interval)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            if looped_through == 1:
                # from the first loop, already traversed the lower pval range of the study
                assert index_marker == 30
            assert_number_of_times_study_is_in_datasets(datasets, 's1', 5)
            assert_studies_from_list(datasets, ['s1'])
            looped_through += 1
            start = start + index_marker

        assert looped_through == 6

    def test_loop_through_s1_size_42(self):
        start = 0
        size = 42
        # second half of s1
        pval_interval = FloatInterval().set_tuple(0.0001, 0.1)

        looped_through = 1

        while True:
            datasets, index_marker = self.searcher.search_study(trait='t1', study='s1', start=start, size=size, pval_interval=pval_interval)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            assert_number_of_times_study_is_in_datasets(datasets, 's1', 25)
            assert_studies_from_list(datasets, ['s1'])

            # comes to the end of the study so it will not go over
            assert index_marker == 50

            looped_through += 1
            start = start + index_marker

        assert looped_through == 2
