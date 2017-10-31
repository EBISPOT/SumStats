import os
import pytest
import sumstats.chr.loader as loader
import sumstats.chr.query_utils as query
from sumstats.chr.constants import *
from tests.chr.test_constants import *
from sumstats.utils.interval import *


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

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_block_groups_from_parent_within_block_range(self):
        chr_group_1 = self.f.get("1")
        chr_group_2 = self.f.get("2")

        with pytest.raises(ValueError):
            bp_interval = IntInterval().set_tuple(1118275, 1118276)
            query.get_block_groups_from_parent_within_block_range(chr_group_1, bp_interval)

        with pytest.raises(TypeError):
            bp_interval = IntInterval().set_tuple(None, 1118276)
            query.get_block_groups_from_parent_within_block_range(chr_group_1, bp_interval)

        with pytest.raises(AttributeError):
            bp_interval = IntInterval().set_tuple(1200000, 1200000)
            query.get_block_groups_from_parent_within_block_range(None, bp_interval)

        bp_interval = IntInterval().set_string_tuple("1200000:1200000")
        blocks = query.get_block_groups_from_parent_within_block_range(chr_group_1, bp_interval)
        assert blocks.__class__ is list
        assert len(blocks) == 1
        assert blocks[0].__class__ == h5py._hl.group.Group

        bp_interval = IntInterval().set_string_tuple("48500000:49200000")
        blocks = query.get_block_groups_from_parent_within_block_range(chr_group_2, bp_interval)
        assert len(blocks) == 8
        assert blocks[0].name == "/2/48500000"
        assert blocks[7].name == "/2/49200000"

        with pytest.raises(ValueError):
            bp_interval = IntInterval().set_string_tuple("49200000:48500000")
            query.get_block_groups_from_parent_within_block_range(chr_group_2, bp_interval)

    def test_get_dsets_from_plethora_of_blocks(self):
        chr_group_2 = self.f.get("/2")

        bp_interval = IntInterval().set_tuple(48500000, 49200000)
        block_groups = query.get_block_groups_from_parent_within_block_range(chr_group_2, bp_interval)

        name_to_dataset = query.get_dsets_from_plethora_of_blocks(block_groups)
        assert name_to_dataset.__class__ is dict

        for dset_name in TO_QUERY_DSETS:
            # 2 values for each of 3 studies that we loaded
            assert len(name_to_dataset[dset_name]) == 6

        bp_interval = IntInterval().set_tuple(48600000, 48600000)
        block_groups = query.get_block_groups_from_parent_within_block_range(chr_group_2, bp_interval)
        name_to_dataset = query.get_dsets_from_plethora_of_blocks(block_groups)
        for dset_name in TO_QUERY_DSETS:
            # no SNP bp falls into this group
            assert len(name_to_dataset[dset_name]) == 0

    def test_get_dsets_group(self):
        chr_group_2 = self.f.get("/2")

        bp_interval = IntInterval().set_tuple(48500000, 48500000)
        block_groups = query.get_block_groups_from_parent_within_block_range(chr_group_2, bp_interval)
        block_group = block_groups[0]

        name_to_dset = query.get_dsets_from_group(block_group)
        assert len(name_to_dset) == len(TO_STORE_DSETS)
        for dset_name, dset in name_to_dset.items():
            if dset_name is STUDY_DSET:
                assert len(set(dset)) == 3
            else:
                assert len(set(dset)) == 1

    def test_get_block_number(self):
        print()
        bp = 0
        block_size = 100000
        assert query.get_block_number(bp) == block_size

        bp = 50000
        assert query.get_block_number(bp) == block_size

        bp = 100000
        assert query.get_block_number(bp) == block_size

        bp = 100001
        assert query.get_block_number(bp) == 2*block_size

        bp = 110000
        assert query.get_block_number(bp) == 2*block_size

        bp = 200000
        assert query.get_block_number(bp) == bp

        bp = 900000
        assert query.get_block_number(bp) == bp

        bp = 900001
        assert query.get_block_number(bp) == 1000000

        bp = 999999
        assert query.get_block_number(bp) == 1000000

        bp = 1100000
        assert query.get_block_number(bp) == bp

        bp = 1100001
        assert query.get_block_number(bp) == 1200000
