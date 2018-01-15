import os
import sumstats.snp.loader as loader
from sumstats.snp.searcher import Search
from tests.prep_tests import *


class TestUnitSearcher(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        self.start = 0
        self.size = 20
        self.query = Search(self.h5file)

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_snp(self):
        snp = "rs7085086"

        self.query.query_for_snp(snp, self.start, self.size)
        datasets = self.query.get_result()

        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 3

        assert len(set(datasets[CHR_DSET])) == 1
        assert set(datasets[CHR_DSET]).pop() == 2
