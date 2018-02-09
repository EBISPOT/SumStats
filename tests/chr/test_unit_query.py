import os

import sumstats.chr.block as bk
import sumstats.chr.loader as loader
import sumstats.chr.search.access.repository as query
from sumstats.chr.constants import *
from sumstats.utils.interval import *
from tests.prep_tests import *


class TestUnitQueryUtils(object):
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
        self.start = 0
        self.size = 20

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_dsets_from_plethora_of_blocks(self):
        chr_group_2 = gu.Group(self.f.get("/2"))

        bp_interval = IntInterval().set_tuple(48500000, 49200000)
        block = bk.Block(bp_interval)
        block_groups = block.get_block_groups_from_parent(chr_group_2)

        datasets = query.load_datasets_from_groups(block_groups, self.start, self.size)
        assert datasets.__class__ is dict

        for dset_name in TO_QUERY_DSETS:
            # 2 values for each of 3 studies that we loaded
            assert len(datasets[dset_name]) == 6

        bp_interval = IntInterval().set_tuple(48600000, 48600000)
        block = bk.Block(bp_interval)
        block_groups = block.get_block_groups_from_parent(chr_group_2)

        datasets = query.load_datasets_from_groups(block_groups, self.start, self.size)
        for dset_name in TO_QUERY_DSETS:
            # no SNP bp falls into this group
            assert len(datasets[dset_name]) == 0

    def test_get_dsets_group(self):
        chr_group_2 = gu.Group(self.f.get("/2"))

        bp_interval = IntInterval().set_tuple(48500000, 48500000)
        block = bk.Block(bp_interval)
        block_groups = block.get_block_groups_from_parent(chr_group_2)

        block_group = next(block_groups)

        datasets = query.get_dsets_from_group(block_group, self.start, self.size)
        assert len(datasets) == len(TO_STORE_DSETS)
        for dset_name, dset in datasets.items():
            if dset_name is STUDY_DSET:
                assert len(set(dset)) == 3
            else:
                assert len(set(dset)) == 1
