import os
import sumstats.snp.loader as loader
import sumstats.snp.searcher as searcher
from sumstats.snp.constants import *
from tests.snp.test_constants import *


class TestFirstApproach(object):
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

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_snp(self):
        snp = "rs7085086"

        name_to_dataset = searcher.query_for_snp(self.f, snp)

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 3

        assert len(set(name_to_dataset[CHR_DSET])) == 1
        assert set(name_to_dataset[CHR_DSET]).pop() == 2
