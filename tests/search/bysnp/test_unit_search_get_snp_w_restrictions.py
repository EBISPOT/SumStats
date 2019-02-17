import sumstats.controller as search
from sumstats.snp.constants import *
from sumstats.utils.interval import *
from tests.search.test_utils import *
import sumstats.utils.dataset_utils as utils
from config import properties


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self):
        # initialize searcher with local path
        properties.h5files_path = "./outputsnp"
        self.searcher = search.Search(properties)

    def test_get_snp_filter_study(self):
        start = 0
        size = 20

        datasets, index_marker = self.searcher.search_snp(snp='rs138808727', start=start, size=size, study='s3')
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 1)
        assert_studies_from_list(datasets, ['s3'])
        # max snp group size
        assert index_marker == 10

    def test_get_snp_filter_lower_pval(self):
        start = 0
        size = 20

        pval_interval = FloatInterval().set_tuple(0.01, 0.01)
        datasets, index_marker = self.searcher.search_snp(snp='rs138808727', start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 3)
        assert_studies_from_list(datasets, ['s1', 's3', 's5'])
        # max snp group size
        assert index_marker == 10

    def test_get_snp_filter_upper_pval(self):
        start = 0
        size = 20

        pval_interval = FloatInterval().set_tuple(0.1, 0.1)
        datasets, index_marker = self.searcher.search_snp(snp='rs138808727', start=start, size=size,
                                                          pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 2)
        assert_studies_from_list(datasets, ['s2', 's4'])
        # max snp group size
        assert index_marker == 10

    def test_get_snp_loop_through_filter_lower_pval(self):
        start = 0
        size = 2
        pval_interval = FloatInterval().set_tuple(0.01, 0.01)

        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

        datasets, index_marker = self.searcher.search_snp(snp='rs138808727', start=start, size=size, pval_interval=pval_interval)
        d = utils.extend_dsets_with_subset(d, datasets)

        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 2)
        assert_studies_from_list(datasets, ['s1', 's3'])
        assert index_marker == 6

        start = start + index_marker
        datasets, index_marker = self.searcher.search_snp(snp='rs138808727', start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 1)

        assert_studies_from_list(datasets, ['s5'])
        d = utils.extend_dsets_with_subset(d, datasets)

        assert len(d[REFERENCE_DSET]) == 3
