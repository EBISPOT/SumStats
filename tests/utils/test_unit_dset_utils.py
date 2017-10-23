import os

import h5py
import numpy as np
import pytest
import sumstats.utils.dset_utils as du


class TestQueryUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_upper_limit_mask(self):
        vector = [1, 2, 3, 4]
        upper_limit = 3
        expected_mask = [True, True, True, False]
        mask = du.get_upper_limit_mask(upper_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = ["1", "2", "3", "4"]
        upper_limit = "2"
        expected_mask = [True, True, False, False]
        mask = du.get_upper_limit_mask(upper_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = ["1", "2", "3", "4"]
        upper_limit = 2
        with pytest.raises(TypeError):
            du.get_upper_limit_mask(upper_limit, vector)

    def test_get_lower_limit_mask(self):
        vector = [1, 2, 3, 4]
        lower_limit = 3
        expected_mask = [False, False, True, True]
        mask = du.get_lower_limit_mask(lower_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = ["1", "2", "3", "4"]
        lower_limit = "2"
        expected_mask = [False, True, True, True]
        mask = du.get_lower_limit_mask(lower_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = ["1", "2", "3", "4"]
        lower_limit = 2
        with pytest.raises(TypeError):
            du.get_lower_limit_mask(lower_limit, vector)

    def test_combine_list_of_masks(self):
        mask1 = [True, True]
        mask2 = [True, False]
        expected_mask = [True, False]
        list_of_masks = [mask1, mask2]
        mask = du.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = [True, False, True]
        expected_mask = [True, False]
        list_of_masks = [mask1, mask2]
        mask = du.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = [True, False, False]
        expected_mask = [True, False]
        list_of_masks = [mask1, mask2]
        mask = du.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = None
        expected_mask = mask1
        list_of_masks = [mask1, mask2]
        mask = du.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = None
        mask2 = [True, True]
        expected_mask = mask2
        list_of_masks = [mask1, mask2]
        mask = du.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = None
        mask2 = None
        expected_mask = None
        list_of_masks = [mask1, mask2]
        mask = du.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

    def test_get_cutoff_mask(self):
        block_floor = 0
        block_ceil = block_size = 100000
        bp_chr_array = np.asarray([0, 100000, 100001, 1, 50000, 200000])
        expected_mask = [True, True, False, True, True, False]
        block_mask = du.interval_mask(block_floor, block_ceil, bp_chr_array)
        assert np.array_equal(expected_mask, block_mask)

        block_floor = block_ceil + 1
        block_ceil += block_size
        bp_chr_array = np.asarray([0, 100000, 100001, 1, 50000, 200000, 200001, 300000])
        expected_mask = [False, False, True, False, False, True, False, False]
        block_mask = du.interval_mask(block_floor, block_ceil, bp_chr_array)
        assert np.array_equal(expected_mask, block_mask)

        with pytest.raises(TypeError):
            du.interval_mask("a", block_ceil, bp_chr_array)

        with pytest.raises(TypeError):
            du.interval_mask(True, block_ceil, bp_chr_array)

        with pytest.raises(TypeError):
            du.interval_mask(0.1, block_ceil, bp_chr_array)

        with pytest.raises(TypeError):
            du.interval_mask(0.1, 0.3, bp_chr_array)

        with pytest.raises(TypeError):
            du.interval_mask(block_floor, "a", bp_chr_array)

        with pytest.raises(TypeError):
            du.interval_mask(block_floor, False, bp_chr_array)

        with pytest.raises(TypeError):
            bp_chr_array = ["a", "b", "c", "d", "d", "d", "d", "d"]
            du.interval_mask(block_floor, block_ceil, bp_chr_array)

    def test_get_equality_mask(self):
        chromosome_array = np.asarray([1, 2, 3, 1])
        with pytest.raises(TypeError):
            du.equality_mask("1", chromosome_array)

        with pytest.raises(TypeError):
            du.equality_mask(True, chromosome_array)

        with pytest.raises(TypeError):
            du.equality_mask(0.1, chromosome_array)

        mask = du.equality_mask(None, chromosome_array)
        expected_mask = None
        assert mask is expected_mask

        mask = du.equality_mask(1, chromosome_array)
        expected_mask = [True, False, False, True]
        assert np.array_equal(expected_mask, mask)

        snp_array = np.asarray(["rs1", "rs1", "rs2", "rs3"])
        mask = du.equality_mask("rs1", snp_array)
        expected_mask = [True, True, False, False]
        assert np.array_equal(expected_mask, mask)

    def test_filter_by_mask(self):
        vector = np.asarray([1, 2, 3, 4])
        mask = [True, False, False, True]
        masked_vector = du.filter_by_mask(vector, mask)
        assert len(masked_vector) == 2
        assert masked_vector[0] == 1
        assert masked_vector[1] == 4

        vector = np.asarray(["a", "b", "c", "d"])
        masked_vector = du.filter_by_mask(vector, mask)
        assert len(masked_vector) == 2
        assert masked_vector[0] == "a"
        assert masked_vector[1] == "d"
