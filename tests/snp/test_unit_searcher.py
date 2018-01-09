import os
import sumstats.snp.loader as loader
from sumstats.snp.searcher import Search
from tests.snp.test_constants import *


class TestUnitSearcher(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq' : frequencyarray}

        load = loader.Loader(None, self.h5file, 'PM001', dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
        load = loader.Loader(None, self.h5file, 'PM002', dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
        load = loader.Loader(None, self.h5file, 'PM003', dict)
        load.load()

        self.start = 0
        self.size = 20
        self.query = Search(self.h5file)

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_snp(self):
        snp = "rs7085086"

        self.query.query_for_snp(snp, self.start, self.size)
        name_to_dataset = self.query.get_result()

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 3

        assert len(set(name_to_dataset[CHR_DSET])) == 1
        assert set(name_to_dataset[CHR_DSET]).pop() == 2
