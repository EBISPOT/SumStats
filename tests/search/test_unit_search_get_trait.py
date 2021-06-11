import sumstats.controller as search
from sumstats.trait.constants import *
from tests.search.test_utils import *
from tests.search.conftest import SINGLE_TRAIT
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

    def test_search_raises_error(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search(trait='EFO_NOTEXISTS', start=start, size=size)
        assert datasets is None
        assert index_marker is start

    def test_search_default_trait_0_20(self):
        start = 0
        size = 20

        datasets, index_marker = self.searcher.search(trait=DEFAULT_TEST_EFO, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 2 * len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))
        assert_studies_from_list(datasets, [DEFAULT_TEST_GCST, 'GCST123457'])
        assert_number_of_times_study_is_in_datasets(datasets, DEFAULT_TEST_GCST, len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))
        assert_number_of_times_study_is_in_datasets(datasets, 'GCST123457', len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))

    def test_search_specific_trait(self):
        start = 0
        size = 200

        datasets, index_marker = self.searcher.search(trait=SINGLE_TRAIT, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))
        assert_studies_from_list(datasets, ['GCST123458'])
        assert_number_of_times_study_is_in_datasets(datasets, 'GCST123458', len(DEFAULT_TEST_DATA_DICT[PVAL_DSET]))
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_loop_through_default_trait_size_2(self):
        start = 0
        size = 2
        datasets, index_marker = self.searcher.search(start=start, size=size, trait=DEFAULT_TEST_EFO)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + size
        new_start = index_marker
        datasets, index_marker = self.searcher.search(start=new_start, size=size, trait=DEFAULT_TEST_EFO)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, size)
        assert index_marker == start + 2 * (size)