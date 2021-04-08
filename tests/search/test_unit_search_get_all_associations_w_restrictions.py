import sumstats.controller as search
import sumstats.utils.dataset_utils as utils
from sumstats.trait.constants import *
from tests.search.test_utils import *
from sumstats.utils.interval import FloatInterval
from config import properties
from tests.search.conftest import TEST_METADATA, SMALL_PVALUE_DATA_DICT, DEFAULT_TEST_DATA_DICT


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self):
        # initialize searcher with local path
        self.searcher = search.Search(properties)
        self.loaded_traits = sorted(list(set([item['efo'] for item in TEST_METADATA])))
        self.loaded_studies = sorted(list(set([item['gcst'] for item in TEST_METADATA])))
        self.size_loaded = len(self.loaded_studies) * len(DEFAULT_TEST_DATA_DICT[PVAL_DSET])

    def test_get_all_loop_through_restrict_pval_to_small(self):
        start = 0
        size = 200
        pval_interval = FloatInterval().set_tuple(0, 0.0001)
        datasets, next_index = self.searcher.search(start=start, size=size, pval_interval=pval_interval)
        print(datasets['p_value'])
        assert_studies_from_list(datasets, ['GCST123458'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, len(SMALL_PVALUE_DATA_DICT['p_value']))


    def test_get_all_loop_through_restrict_pval_to_specific(self):
        start = 0
        size = 200
        pval_interval = FloatInterval().set_tuple(0.00000000000001, 0.00000000000001)
        datasets, next_index = self.searcher.search(start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 1)
        assert_studies_from_list(datasets, ['GCST123458'])

    def test_get_10_with_pval_greater_than_small(self):
        start = 0
        size = 10
        pval_interval = FloatInterval().set_tuple(0.0000000000001, 0.999)

        datasets, next_index = self.searcher.search(start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 10)

    def test_loop_through_w_restrinction_and_always_get_size_2_results(self):
        start = 0
        size = 2

        pval_interval = FloatInterval().set_tuple(0.0001, 0.999)
        datasets, index_marker = self.searcher.search(start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(start=new_start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + 2 * (size)