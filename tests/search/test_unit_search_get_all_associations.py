import sumstats.controller as search
from sumstats.trait.constants import *
from tests.search.test_utils import *
from config import properties
from tests.search.conftest import TEST_METADATA, DEFAULT_TEST_GCST, DEFAULT_TEST_DATA_DICT


class TestLoader(object):

    start = 0
    size = 20

    def setup_method(self):
        # initialize searcher with local path
        self.searcher = search.Search(properties)
        self.loaded_traits = sorted(list(set([item['efo'] for item in TEST_METADATA])))
        self.loaded_studies = sorted(list(set([item['gcst'] for item in TEST_METADATA])))
        self.size_loaded = len(self.loaded_studies) * len(DEFAULT_TEST_DATA_DICT[PVAL_DSET])

    def test_start_0_size_0(self):
        datasets, index_marker = self.searcher.search(start=0, size=0)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)

    def test_get_all(self):
        datasets, index_marker = self.searcher.search(start=0, size=self.size_loaded)
        assert_studies_from_list(datasets, self.loaded_studies)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, self.size_loaded)
        assert_number_of_times_study_is_in_datasets(datasets, DEFAULT_TEST_GCST, len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))

    def test_get_all_size_bigger_than_existing_data(self):
        datasets, index_marker = self.searcher.search(start=0, size=self.size_loaded + 1)
        assert_studies_from_list(datasets, self.loaded_studies)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, self.size_loaded)
        assert_number_of_times_study_is_in_datasets(datasets, DEFAULT_TEST_GCST, len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))

    def test_get_all_loop_through_size_20(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search(start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        start = start + index_marker
        datasets, index_marker = self.searcher.search(start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, self.size_loaded - size)

    def test_get_out_of_bounds(self):
        start = 250
        size = 20
        # empty
        datasets, index_marker = self.searcher.search(start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)

    def test_index_marker(self):
        start = 0
        size = 2
        datasets, index_marker = self.searcher.search(start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(start=new_start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + 2 * (size)