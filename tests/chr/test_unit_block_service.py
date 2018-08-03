import os

import pytest

import sumstats.chr.loader as loader
from sumstats.chr.search.access.block_service import *
from sumstats.utils.interval import *
from tests.prep_tests import *


class TestUnitBlockService(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self):

        # chrarray = [1, 1, 2, 2]
        # bparray = [1118275, 1120431, 49129966, 48480252]
        # pvalsarray = ["0.4865", "0.4314", "0.5986", "0.07057"]
        # loading 3 ranges 1200000 with 2 elements, 49129966 with one element, and  49200000 with one element
        # loading 3 times, once per study

        # requesting only lower range should bring back 6 elements (2 elements times 3 studies)
        # requesting only one of the upper ranges should bring back 3 elements
        # requesting both the 2 upper ranges should bring back 6 elements

        # requesting for only 1 specific bp location should return 3 elements, one for each study

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        self.start = 0
        self.size = 20
        self.service = BlockService(self.h5file)

    def teardown_method(self):
        os.remove(self.h5file)

    def test_query_with_two_blocks_in_range(self):

        block_lower_limit = 48480252
        block_upper_limit = 49129966
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)

        self.service.query("2", bp_interval, self.start, self.size)
        datasets = self.service.get_result()

        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 6

    def test_query_raises_error_when_lower_limit_higher_than_upper_limit(self):

        block_lower_limit = 49129966
        block_upper_limit = 48480252
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        with pytest.raises(ValueError):
            self.service.query("2", bp_interval, self.start, self.size)

    def test_query_upper_limit_on_edge(self):

        block_lower_limit = 49129966
        block_upper_limit = 49200000
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        self.service.query("2", bp_interval, self.start, self.size)
        datasets = self.service.get_result()

        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 3

    def test_query_with_none_upper_block_limit(self):

        block_lower_limit = 49129966
        block_upper_limit = None
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        self.service.query("2", bp_interval, self.start, self.size)
        datasets = self.service.get_result()

        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 3

    def test_query_with_lower_block_range(self):
        block_lower_limit = 1118275
        block_upper_limit = 1120431

        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        self.service.query("1", bp_interval, self.start, self.size)
        datasets = self.service.get_result()
        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 6

        assert len(set(datasets[BP_DSET])) == 2

    def test_query_with_exact_bp_location(self):
        block_lower_limit = 1118275
        block_upper_limit = 1118275

        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)

        self.service.query("1", bp_interval, self.start, self.size)
        datasets = self.service.get_result()

        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 3

        assert len(set(datasets[BP_DSET])) == 1

    def test_query_with_none_lower_block_limit(self):
        block_lower_limit = None
        block_upper_limit = 49129966
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        self.service.query("2", bp_interval, self.start, self.size)
        datasets = self.service.get_result()

        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 3

    def test_query_with_upper_equals_lower_equals_block_limits(self):
        block_lower_limit = 1200000
        block_upper_limit = 1200000
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        self.service.query("1", bp_interval, self.start, self.size)
        datasets = self.service.get_result()

        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 0

    def test_apply_restrictions(self):
        block_lower_limit = 1120431
        block_upper_limit = 1120431
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        self.service.query("1", bp_interval, self.start, self.size)
        pval_interval = FloatInterval().set_tuple(0.5, None)
        self.service.apply_restrictions(pval_interval=pval_interval)
        datasets = self.service.get_result()

        assert len(datasets[REFERENCE_DSET]) == 0

    def test_apply_restrictions_accross_blocks(self):
        block_lower_limit = 0
        block_upper_limit = 1120431
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        self.service.query("1", bp_interval, self.start, self.size)
        pval_interval = FloatInterval().set_tuple(0.48, None)
        self.service.apply_restrictions(pval_interval=pval_interval)
        datasets = self.service.get_result()

        assert len(datasets[REFERENCE_DSET]) == 3

    def test_get_block_range_size_one_block(self):
        block_lower_limit = 49129966
        block_upper_limit = 49129966
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        # for chromosome 2 this block has been loaded 3 times (once for each study)

        block_range_size = self.service.get_block_range_size(2, bp_interval)
        assert block_range_size == 3

    def test_get_block_range_size_two_blocks(self):
        block_lower_limit = 48480252
        block_upper_limit = 49129966
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        # for chromosome 2, each block has been loaded 3 times (once for each study)

        block_range_size = self.service.get_block_range_size(2, bp_interval)
        assert block_range_size == 6

