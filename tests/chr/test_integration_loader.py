import os
import pytest
import numpy as np
import sumstats.chr.loader as loader
from tests.prep_tests import *
from sumstats.chr.constants import *


class TestLoader(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_chromosome_groups(self):
        chr_group_1 = self.f.get("1")
        assert chr_group_1 is not None
        assert len(chr_group_1.keys()) == 12

        chr_group_2 = self.f.get("2")
        assert chr_group_2 is not None

        chr_group_3 = self.f.get("3")
        assert chr_group_3 is None

    def test_block_groups(self):
        chr_group_1 = self.f.get("1")

        block1 = chr_group_1.get("1200000")
        assert block1 is not None
        assert block1.name == "/1/1200000"

        assert len(block1.keys()) != 0

        block0 = chr_group_1.get("100000")
        assert len(block0.keys()) == 0

        chr_group_2 = self.f.get("2")

        blocks = list(chr_group_2.keys())
        assert len(blocks) != 0

        assert blocks[0] == "100000"
        assert max(np.array(list((blocks)), dtype=int)) == 49200000

    def test_snps_in_blocks(self):
        block11 = self.f.get("/1/1200000")
        datasets = list(block11.keys())
        assert len(datasets) == len(TO_STORE_DSETS)
        for dset_name in TO_STORE_DSETS:
            dataset = block11.get(dset_name)
            assert dataset is not None
            assert len(dataset[:]) > 0
        assert "rs11250701" in block11.get(SNP_DSET)[:]

        block21 = self.f.get("/2/48500000")
        datasets = list(block21.keys())
        assert len(datasets) == len(TO_STORE_DSETS)
        for dset_name in TO_STORE_DSETS:
            dataset = block11.get(dset_name)
            assert dataset is not None
            assert len(dataset[:]) > 0
        assert "rs7085086" in block21.get(SNP_DSET)[:]

        block22 = self.f.get("/2/49200000")
        datasets = list(block22.keys())
        assert len(datasets) == len(TO_STORE_DSETS)
        for dset_name in TO_STORE_DSETS:
            dataset = block11.get(dset_name)
            assert dataset is not None
            assert len(dataset[:]) > 0
        assert "rs12345" in block22.get(SNP_DSET)[:]

    def test_block_group_content(self):
        block1 = self.f.get("/1/1200000")
        snp_dset = block1.get(SNP_DSET)[:].tolist()
        snp = "rs185339560"
        assert snp in snp_dset

        snps_index = snp_dset.index(snp)

        mantissa_dset = block1.get(MANTISSA_DSET)[:].tolist()
        assert mantissa_dset[snps_index] == 4.865

        exp_dset = block1.get(EXP_DSET)[:]
        assert exp_dset[snps_index] == -1

        studies_dset = block1.get(STUDY_DSET)[:].tolist()
        assert "PM001" in studies_dset
        assert "PM002" in studies_dset
        assert "PM003" in studies_dset

    def test_get_block_group_from_block_ceil(self):
        chr_group = self.f.get("1")
        block_group = loader.get_block_group_from_block_ceil(chr_group, BLOCK_SIZE)
        assert str(BLOCK_SIZE) in  block_group.name

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
