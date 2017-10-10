import os
import h5py
import pytest
import numpy as np
import sumstats.chr.loader as loader
import sumstats.chr.searcher as searcher


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
        pvalsarray = [0.4865, 0.4314, 0.5986, 0.7057]
        chrarray = [1, 1, 2, 2]
        orarray = [0.92090, 1.01440, 0.97385, 0.99302]
        bparray = [1118275, 1120431, 49129966, 48480252]
        effect_array = ["A", "B", "C", "D"]
        other_array = ["Z", "Y", "X", "W"]

        dict = {}
        dict["snp"] = snpsarray
        dict["pval"] = pvalsarray
        dict["chr"] = chrarray
        dict["or"] = orarray
        dict["bp"] = bparray
        dict["effect"] = effect_array
        dict["other"] = other_array

        load = loader.Loader(None, self.h5file, 'PM001', dict)
        load.load()
        load = loader.Loader(None, self.h5file, 'PM002', dict)
        load.load()
        load = loader.Loader(None, self.h5file, 'PM003', dict)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_block_range(self):
        chr_group = self.f.get("/2")
        block_lower_limit = 48480252
        block_upper_limit = 49129966
        dict_of_dsets = searcher.query_for_block_range(chr_group, block_lower_limit, block_upper_limit)

        assert dict_of_dsets.__class__ is dict

        for dset_name in dict_of_dsets:
            assert len(dict_of_dsets[dset_name]) == 6

        block_lower_limit = 49129966
        block_upper_limit = 48480252
        with pytest.raises(ValueError):
            searcher.query_for_block_range(chr_group, block_lower_limit, block_upper_limit)

        block_lower_limit = 49129966
        block_upper_limit = 49200000
        dict_of_dsets = searcher.query_for_block_range(chr_group, block_lower_limit, block_upper_limit)

        assert dict_of_dsets.__class__ is dict

        for dset_name in dict_of_dsets:
            assert len(dict_of_dsets[dset_name]) == 3

    def test_query_for_snp(self):
        chr_group = self.f.get("/2")
        block_number = 48500000
        snp = "rs7085086"

        dict_of_dsets = searcher.query_for_snp(chr_group, block_number, snp)

        assert dict_of_dsets.__class__ is dict

        for dset_name in dict_of_dsets:
            assert len(dict_of_dsets[dset_name]) == 3

        assert len(set(dict_of_dsets['snp'])) == 1
        assert set(dict_of_dsets['snp']).pop() == snp
