import sumstats.controller as search
from sumstats.trait.constants import *
from tests.search.test_utils import *
from config import properties
from tests.search.conftest import TEST_METADATA, DEFAULT_TEST_GCST, DEFAULT_TEST_DATA_DICT, DEFAULT_TEST_EFO


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self):
        self.searcher = search.Search(properties)
        self.loaded_traits = sorted(list(set([item['efo'] for item in TEST_METADATA])))
        self.loaded_studies = sorted(list(set([item['gcst'] for item in TEST_METADATA])))
        self.size_loaded = len(self.loaded_studies) * len(DEFAULT_TEST_DATA_DICT[PVAL_DSET])

    def test_search_default_study_0_2(self):
        start = 0
        size = 2
        datasets, index_marker = self.searcher.search(trait=DEFAULT_TEST_EFO, study=DEFAULT_TEST_GCST, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert_studies_from_list(datasets, [DEFAULT_TEST_GCST])

    def test_search_default_study_0_20(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search(trait=DEFAULT_TEST_EFO, study=DEFAULT_TEST_GCST, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))
        assert_studies_from_list(datasets, [DEFAULT_TEST_GCST])

    def test_search_default_study_start_midway(self):
        start = 2
        size = 20

        datasets, index_marker = self.searcher.search(trait=DEFAULT_TEST_EFO, study=DEFAULT_TEST_GCST, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]) - start)
        assert_studies_from_list(datasets, [DEFAULT_TEST_GCST])

    def test_loop_through_default_study_size_2(self):
        start = 0
        size = 2
        datasets, index_marker = self.searcher.search(trait=DEFAULT_TEST_EFO, study=DEFAULT_TEST_GCST, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(trait=DEFAULT_TEST_EFO, study=DEFAULT_TEST_GCST, start=new_start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + 2 * (size)