import sumstats.controller as search
from sumstats.chr.constants import *
from tests.search.test_utils import *
from config import properties
from tests.search.conftest import TEST_METADATA, DEFAULT_TEST_DATA_DICT


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

    def test_get_chromosome_raises_error(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search(chromosome=24, start=start, size=size)
        assert datasets is None
        assert index_marker is start

    def test_get_loaded_chromosome(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search(chromosome=10, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert index_marker == 20

    def test_get_chromosome_loop_through_size_2(self):
        start = 0
        size = 2
        datasets, index_marker = self.searcher.search(start=start, size=size, chromosome=10)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(start=new_start, size=size, chromosome=10)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + 2 * (size)