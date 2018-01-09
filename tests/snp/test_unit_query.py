import os
import sumstats.snp.loader as loader
import sumstats.snp.query as query
from tests.snp.test_constants import *


class TestUnitQueryUtils(object):
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
        self.start = 0
        self.size = 20

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_dsets_group(self):
        snp_group = self.f.get("rs7085086")

        name_to_dset = query.get_dsets_from_group(snp_group, self.start, self.size)
        assert len(name_to_dset) == 9
        for dset_name, dset in name_to_dset.items():
            if dset_name is "study":
                assert len(set(dset)) == 3
            else:
                assert len(set(dset)) == 1

