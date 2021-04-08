import sumstats.controller as search
import tests.search.search_test_constants as search_arrays
from tests.prep_tests import *
from sumstats.chr.constants import *
from tests.search.test_utils import *
import sumstats.utils.dataset_utils as utils
from sumstats.errors.error_classes import *
import pytest
from config import properties


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self):
        # initialize searcher with local path
        self.searcher = search.Search(properties)

    def test_get_chromosome_raises_error(self):
        with pytest.raises(NotFoundError):
            self.searcher.search_chromosome(chromosome=24, start=0, size=20)

    def test_get_chromosome_1_0_20(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_in_list(datasets, ['s1', 's3'])
        assert index_marker == 20
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_20_40(self):
        start = 20
        size = 20
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1', 's3'])
        assert index_marker == 20
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_40_60(self):
        start = 40
        size = 20
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1', 's3'])
        assert index_marker == 20
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_loop_through_size_5(self):
        start = 0
        size = 5

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1', 's3'])
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 5)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 21
        # 100 unique variants
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET]) == 100

    def test_get_chromosome_1_loop_through_size_20(self):
        start = 0
        size = 20

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1', 's3'])
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 6
        # 100 unique variants
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])

    def test_get_chromosome_1_loop_through_size_50(self):
        start = 0
        size = 50

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1', 's3'])
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 3
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])