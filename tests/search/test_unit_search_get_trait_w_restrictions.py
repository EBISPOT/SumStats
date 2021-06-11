import sumstats.controller as search
import sumstats.utils.dataset_utils as utils
from sumstats.trait.constants import *
from tests.search.test_utils import *
from sumstats.utils.interval import *
from config import properties
from tests.search.conftest import SINGLE_TRAIT
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

    def test_search_default_trait_0_20_lower_pval(self):
        start = 0
        size = 20
        pval_interval = FloatInterval().set_tuple(0, 0.1)
        datasets, index_marker = self.searcher.search(trait=DEFAULT_TEST_EFO, start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 4)
        assert_studies_from_list(datasets, [DEFAULT_TEST_GCST, 'GCST123457'])
        assert index_marker == start + 4

    def test_search_specific_trait_0_50_lower_pval(self):
        start = 0
        size = 50
        pval_interval = FloatInterval().set_tuple(0, 0.0001)
        datasets, index_marker = self.searcher.search(trait=SINGLE_TRAIT, start=start, size=size, pval_interval=pval_interval)
        print(datasets)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))
        assert_studies_from_list(datasets, ['GCST123458'])
        assert index_marker == start + len(DEFAULT_TEST_DATA_DICT[PVAL_DSET])
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])


    def test_search_default_trait_returns_empty(self):
        start = 0
        size = 20

        pval_interval = FloatInterval().set_tuple(0, 0.0001)
        datasets, index_marker = self.searcher.search(trait=DEFAULT_TEST_EFO, start=start, size=size, pval_interval=pval_interval)
        assert datasets is None
        assert index_marker == start

    def test_loop_through_default_trait_size_2_w_restriction(self):
        start = 0
        size = 2
        pval_interval = FloatInterval().set_tuple(0, 0.1)
        datasets, index_marker = self.searcher.search(start=start, size=size, trait=DEFAULT_TEST_EFO, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(start=new_start, size=size, trait=DEFAULT_TEST_EFO, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + 2 * (size)