import os
import pytest
import sumstats.chr.loader as loader
from sumstats.chr.searcher import Search
from sumstats.chr.constants import *
from tests.chr.test_constants import *
from sumstats.utils.interval import *


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

    def test_query_for_chromosome(self):
        self.query.query_for_chromosome("2", self.start, self.size)
        name_to_dataset = self.query.get_result()

        assert len(name_to_dataset[BP_DSET]) == 6
        assert len(name_to_dataset[SNP_DSET]) == 6

    def test_query_for_block_range(self):

        block_lower_limit = 48480252
        block_upper_limit = 49129966
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)

        self.query.query_chr_for_block_range("2", bp_interval, self.start, self.size)
        name_to_dataset = self.query.get_result()

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 6

        block_lower_limit = 49129966
        block_upper_limit = 48480252
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        with pytest.raises(ValueError):
            self.query.query_chr_for_block_range("2", bp_interval, self.start, self.size)

        block_lower_limit = 49129966
        block_upper_limit = 49200000
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        self.query.query_chr_for_block_range("2", bp_interval, self.start, self.size)
        name_to_dataset = self.query.get_result()

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 3

