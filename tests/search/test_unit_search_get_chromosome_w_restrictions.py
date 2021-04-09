import sumstats.controller as search
from sumstats.utils.interval import *
from sumstats.chr.constants import *
from tests.search.test_utils import *
from config import properties
from tests.search.conftest import TEST_METADATA, DEFAULT_TEST_GCST, DEFAULT_TEST_DATA_DICT


class TestLoader(object):
    file = None
    start = 0
    size = 20

    def setup_method(self):
        self.searcher = search.Search(properties)
        self.loaded_traits = sorted(list(set([item['efo'] for item in TEST_METADATA])))
        self.loaded_studies = sorted(list(set([item['gcst'] for item in TEST_METADATA])))
        self.size_loaded = len(self.loaded_studies) * len(DEFAULT_TEST_DATA_DICT[PVAL_DSET])

    def test_get_chromosome_1_0_50_default_study(self):
        start = 0
        size = 50
        size_loaded = len(DEFAULT_TEST_DATA_DICT[PVAL_DSET])
        datasets, index_marker = self.searcher.search(chromosome=10, start=start, size=size, study=DEFAULT_TEST_GCST)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size_loaded)
        assert_studies_from_list(datasets, [DEFAULT_TEST_GCST])
        assert index_marker == size_loaded
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_0_50_default_study_lower_pval(self):
        start = 0
        size = 50
        size_loaded = 2
        pval_interval = FloatInterval().set_tuple(0.00001, 0.1)
        datasets, index_marker = self.searcher.search(chromosome=10, start=start, size=size, study=DEFAULT_TEST_GCST, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size_loaded)
        assert_studies_from_list(datasets, [DEFAULT_TEST_GCST])
        assert index_marker == size_loaded
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])


    def test_get_chromosome_loop_through_size_2_default_study(self):
        start = 0
        size = 2
        datasets, index_marker = self.searcher.search(start=start, size=size, chromosome=10, study=DEFAULT_TEST_GCST)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(start=new_start, size=size, chromosome=10, study=DEFAULT_TEST_GCST)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + 2 * (size)

    def test_get_chromosome_loop_through_size_2_lower_pval(self):
        start = 0
        size = 2
        pval_interval = FloatInterval().set_tuple(0.00001, 0.1)
        datasets, index_marker = self.searcher.search(start=start, size=size, chromosome=10, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(start=new_start, size=size, chromosome=10, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + 2 * (size)