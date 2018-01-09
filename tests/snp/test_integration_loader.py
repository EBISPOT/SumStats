import os
import pytest
import sumstats.snp.loader as loader
from tests.snp.test_constants import *


class TestLoader(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

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

    def test_snp_group(self):
        snp_group = self.f.get("/rs185339560")
        assert snp_group is not None

        snp_group = self.f.get("/rs7085086")
        assert snp_group is not None

    def test_snp_group_content(self):
        snp1 = self.f.get("/rs185339560")
        assert snp1 is not None
        info = list(snp1.keys())
        assert len(info) == len(TO_STORE_DSETS)

        chr = snp1.get(CHR_DSET)
        assert len(chr[:]) == 3  # loaded 3 times for 3 diff studies
        assert chr[:][0] == 1

        mantissa = snp1.get(MANTISSA_DSET)
        assert len(mantissa[:]) == 3  # loaded 3 times for 3 diff studies
        assert mantissa[:][0] == 4.865

        exp = snp1.get(EXP_DSET)
        assert len(exp[:]) == 3  # loaded 3 times for 3 diff studies
        assert exp[:][0] == -1

        studies = snp1.get(STUDY_DSET)
        assert len(studies[:]) == 3
        assert studies[:][0] == "PM001"
        assert studies[:][1] == "PM002"
        assert studies[:][2] == "PM003"

    def test_study_already_loaded_raises_error(self):

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, 'PM001', dict)
        with pytest.raises(ValueError):
            load.load()

    def test_study_already_loaded_doesnt_raise_error_on_new_study(self):
        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, 'PM004', dict)
        load.load()