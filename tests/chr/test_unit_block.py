import sumstats.chr.block as bk
import pytest
from sumstats.utils.interval import *
from tests.prep_tests import *
import sumstats.chr.loader as loader
import os


class TestUnitQueryUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self):

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
        self.chr_group_1 = self.f.get("1")
        self.chr_group_2 = self.f.get("2")

    def teardown_method(self):
        os.remove(self.h5file)

    def test_get_block_groups_from_parent_raises_error_when_parent_missing(self):

        with pytest.raises(AttributeError):
            bp_interval = IntInterval().set_tuple(1200000, 1200000)
            block = bk.Block(bp_interval)
            block.get_block_groups_from_parent(None)

    def test_get_block_groups_from_parent_raises_error_when_lower_limit_bigger_than_upper_limit(self):
        with pytest.raises(ValueError):
            bp_interval = IntInterval().set_string_tuple("49200000:48500000")
            block = bk.Block(bp_interval)
            block.get_block_groups_from_parent(self.chr_group_2)

    def test_get_block_groups_from_parent(self):
        bp_interval = IntInterval().set_string_tuple("1200000:1200000")
        block = bk.Block(bp_interval)
        chrgroup_1 = gu.Group(self.chr_group_1)
        blocks = block.get_block_groups_from_parent(chrgroup_1)

        assert blocks.__class__ is list
        assert len(blocks) == 1
        assert blocks[0].__class__ == gu.Group

    def test_get_block_number(self):
        print()
        bp = 0
        block_size = 100000
        assert bk.get_block_number(bp) == block_size

        bp = 50000
        assert bk.get_block_number(bp) == block_size

        bp = 100000
        assert bk.get_block_number(bp) == block_size

        bp = 100001
        assert bk.get_block_number(bp) == 2 * block_size

        bp = 110000
        assert bk.get_block_number(bp) == 2 * block_size

        bp = 200000
        assert bk.get_block_number(bp) == bp

        bp = 900000
        assert bk.get_block_number(bp) == bp

        bp = 900001
        assert bk.get_block_number(bp) == 1000000

        bp = 999999
        assert bk.get_block_number(bp) == 1000000

        bp = 1100000
        assert bk.get_block_number(bp) == bp

        bp = 1100001
        assert bk.get_block_number(bp) == 1200000