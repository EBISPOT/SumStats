import shutil

import sumstats.search as search
from sumstats.chr.constants import *
from tests.search.test_utils import *
from sumstats.utils.interval import *
import sumstats.utils.utils as utils


class TestLoader(object):
    file = None
    start = 0
    size = 20

    def setup_method(self, method):
        # initialize searcher with local path
        self.searcher = search.Search(path="./outputchr")

    def test_get_chromosome_1_first_range_s3(self):
        start = 0
        size = 200
        bp_interval = IntInterval().set_string_tuple("0:1200000")
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, bp_interval=bp_interval, start=start, size=size, study='s3')
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 25)
        assert_studies_from_list(datasets, ['s3'])
        # chromosome 1 with bp interval 0:1200000 has only 50 elements anyway
        assert index_marker == 200
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_first_range_s3_upper_pval(self):
        start = 0
        size = 200
        bp_interval = IntInterval().set_string_tuple("48500000:49200000")
        pval_interval = FloatInterval().set_tuple(0.1, 0.1)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, bp_interval=bp_interval, start=start,
                                                                 size=size, study='s3', pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 10)
        assert index_marker == 200

    def test_get_chromosome_1_first_range_s3_lower_pval(self):
        start = 0
        size = 200
        bp_interval = IntInterval().set_string_tuple("0:1200000")
        pval_interval = FloatInterval().set_tuple(0.00001, 0.01)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, bp_interval=bp_interval, start=start,
                                                                 size=size, study='s3', pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 25)
        assert_studies_from_list(datasets, ['s3'])
        assert index_marker == 200
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chr_1_second_range_loop_5_s3(self):
        start = 0
        size = 5

        bp_interval = IntInterval().set_string_tuple("1200001:49200000")

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval, study='s3')
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_from_list(datasets, ['s3'])
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 5)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval, study='s3')
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 6
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])

    def test_get_chr_1_second_range_loop_20_upper_pval(self):
        start = 0
        size = 20

        # index 25-40 for first non-empty block: 48500000
        # index 40-50 for second non-empty block: 49200000
        bp_interval = IntInterval().set_string_tuple("1200001:49200000")
        # index 20-35
        pval_interval = FloatInterval().set_tuple(0.1, 0.1)
        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval, pval_interval=pval_interval)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1','s3'])

            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
            start = start + index_marker

            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size, bp_interval=bp_interval, pval_interval=pval_interval)
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 2
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET]) == 20
