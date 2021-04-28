import sumstats.controller as search
from sumstats.trait.constants import *
from tests.search.test_utils import *
from sumstats.utils.interval import *
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

    def test_search_default_study_0_20_lower_pval(self):
        start = 0
        size = 20
        pval_interval = FloatInterval().set_tuple(0.00001, 0.1)
        datasets, index_marker = self.searcher.search(study=DEFAULT_TEST_GCST, start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 2)
        assert_studies_from_list(datasets, [DEFAULT_TEST_GCST])
        assert index_marker == 2

    def test_search_lower_pval_start_midway(self):
        start = 4
        size = 20
        pval_interval = FloatInterval().set_tuple(0, 0.0001)
        datasets, index_marker = self.searcher.search(study='GCST123458', start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]) - start)
        assert_studies_from_list(datasets, ['GCST123458'])
        assert index_marker == len(DEFAULT_TEST_DATA_DICT[PVAL_DSET])


    def test_loop_through_default_study_size_2(self):
        start = 0
        size = 2
        pval_interval = FloatInterval().set_tuple(0, 0.1)

        datasets, index_marker = self.searcher.search(study=DEFAULT_TEST_GCST, start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(study=DEFAULT_TEST_GCST, start=new_start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)
        assert index_marker == start + 2
