import sumstats.controller as search
from sumstats.chr.constants import *
from tests.search.test_utils import *
from sumstats.utils.interval import *
import sumstats.utils.dataset_utils as utils
from config import properties


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self, method):
        # initialize searcher with local path
        properties.h5files_path = "./outputchr"
        self.searcher = search.Search(properties)

    def test_get_chromosome_1_first_range(self):
        start = 0
        size = 200
        bp_interval = IntInterval().set_string_tuple("0:1200000")
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, bp_interval=bp_interval, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)
        assert_studies_from_list(datasets, ['s1', 's3'])
        # max block range size
        assert index_marker == 50
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_second_range(self):
        start = 0
        size = 200
        bp_interval = IntInterval().set_string_tuple("1200001:49200000")
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, bp_interval=bp_interval, start=start,
                                                                 size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)
        assert_studies_from_list(datasets, ['s1', 's3'])
        # max block range size
        assert index_marker == 50
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chr_1_second_range_loop_5(self):
        start = 0
        size = 5

        bp_interval = IntInterval().set_string_tuple("1200001:49200000")

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1', 's3'])
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 5)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 11
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])

    def test_get_chr_1_second_range_loop_20(self):
        start = 0
        size = 20

        bp_interval = IntInterval().set_string_tuple("1200001:49200000")

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1','s3'])
            if looped_through <= 2:
                assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
            else:
                assert_datasets_have_size(datasets, TO_QUERY_DSETS, 10)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 4
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])

    def test_get_chr_1_second_range_loop_50(self):
        start = 0
        size = 50

        bp_interval = IntInterval().set_string_tuple("1200001:49200000")

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1', 's3'])

            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)

            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 2
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])


