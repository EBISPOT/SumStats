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
        pvalsarray = ["0.4865", "0.4314", "0.5986", "0.7057"]
        chrarray = ["1", "1", "2", "2"]
        orarray = ["0.92090", "1.01440", "0.97385", "0.99302"]
        bparray = ["1118275", "1120431", "49129966", "48480252"]
        effectarray = ["A", "B", "C", "D"]
        other_array = ["Z", "Y", "X", "W"]
        frequencyarray = ["3.926e-01", "4.900e-03", "1.912e-01", "7.000e-04"]

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": other_array, 'freq' : frequencyarray}

        load = loader.Loader(None, self.h5file, 'PM001', dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": other_array, 'freq': frequencyarray}
        load = loader.Loader(None, self.h5file, 'PM002', dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": other_array, 'freq': frequencyarray}
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
        name_to_dataset = searcher.query_for_block_range(chr_group, block_lower_limit, block_upper_limit)

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 6

        block_lower_limit = 49129966
        block_upper_limit = 48480252
        with pytest.raises(ValueError):
            searcher.query_for_block_range(chr_group, block_lower_limit, block_upper_limit)

        block_lower_limit = 49129966
        block_upper_limit = 49200000
        name_to_dataset = searcher.query_for_block_range(chr_group, block_lower_limit, block_upper_limit)

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 3

    def test_query_for_snp(self):
        chr_group = self.f.get("/2")
        block_number = 48500000
        snp = "rs7085086"

        name_to_dataset = searcher.query_for_snp(chr_group, block_number, snp)

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 3

        assert len(set(name_to_dataset['snp'])) == 1
        assert set(name_to_dataset['snp']).pop() == snp
