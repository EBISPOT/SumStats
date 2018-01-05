import os
import h5py
import pytest
from sumstats.utils.dataset import *

vector_int = Dataset([1, 2, 3, 4])
vector_str = Dataset(["1", "2", "3", "4"])


class TestUnitDataset(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode='a')

    def teardown_method(self, method):
        os.remove(self.h5file)

    def get_upper_limit_int_mask(self):
        upper_limit = 3
        expected_mask = [True, True, True, False]
        mask = vector_int.get_upper_limit_mask(upper_limit)
        assert np.array_equal(expected_mask, mask)

    def get_upper_limit_str_mask(self):
        upper_limit = "2"
        expected_mask = [True, True, False, False]
        mask = vector_str.get_upper_limit_mask(upper_limit)
        assert np.array_equal(expected_mask, mask)

    def get_upper_limit_raises_type_error(self):
        upper_limit = 2
        with pytest.raises(TypeError):
            vector_str.get_upper_limit_mask(upper_limit)

    def get_lower_limit_int_mask(self):
        lower_limit = 3
        expected_mask = [False, False, True, True]
        mask = vector_int.get_lower_limit_mask(lower_limit)
        assert np.array_equal(expected_mask, mask)

    def get_lower_limit_str_mask(self):
        lower_limit = "2"
        expected_mask = [False, True, True, True]
        mask = vector_str.get_lower_limit_mask(lower_limit)
        assert np.array_equal(expected_mask, mask)

    def get_lower_limit_raises_type_error(self):
        lower_limit = 2
        with pytest.raises(TypeError):
            vector_str.get_lower_limit_mask(lower_limit)

    def combine_list_of_same_size_masks(self):
        mask1 = [True, True]
        mask2 = [True, False]
        expected_mask = [True, False]
        list_of_masks = [mask1, mask2]
        mask = logical_and_on_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

    def combine_list_of_not_same_size_masks(self):
        mask1 = [True, True]
        mask2 = [True, False, True]
        expected_mask = [True, False]
        list_of_masks = [mask1, mask2]
        mask = logical_and_on_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

    def combine_mask_with_none_mask(self):
        mask1 = [True, True]
        mask2 = None
        expected_mask = mask1
        list_of_masks = [mask1, mask2]
        mask = logical_and_on_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

    def combine_none_masks(self):
        mask1 = None
        mask2 = None
        expected_mask = None
        list_of_masks = [mask1, mask2]
        mask = logical_and_on_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

    def get_cutoff_mask(self):
        block_floor = 0
        block_ceil = block_size = 100000
        bp_chr_array = Dataset([0, 100000, 100001, 1, 50000, 200000])
        expected_mask = [True, True, False, True, True, False]
        block_mask = bp_chr_array.interval_mask(block_floor, block_ceil)
        assert np.array_equal(expected_mask, block_mask)

        block_floor = block_ceil + 1
        block_ceil += block_size
        bp_chr_array = Dataset([0, 100000, 100001, 1, 50000, 200000, 200001, 300000])
        expected_mask = [False, False, True, False, False, True, False, False]
        block_mask = bp_chr_array.interval_mask(block_floor, block_ceil)
        assert np.array_equal(expected_mask, block_mask)

        with pytest.raises(TypeError):
            bp_chr_array.interval_mask("a", block_ceil)

        with pytest.raises(TypeError):
            bp_chr_array.interval_mask(True, block_ceil)

        with pytest.raises(TypeError):
            bp_chr_array.interval_mask(0.1, block_ceil)

        with pytest.raises(TypeError):
            bp_chr_array.interval_mask(0.1, 0.3)

        with pytest.raises(TypeError):
            bp_chr_array.interval_mask(block_floor, "a")

        with pytest.raises(TypeError):
            bp_chr_array.interval_mask(block_floor, False)

        with pytest.raises(TypeError):
            bp_chr_array = Dataset(["a", "b", "c", "d", "d", "d", "d", "d"])
            bp_chr_array.interval_mask(block_floor, block_ceil)

    def get_equality_mask(self):
        chromosome_array = Dataset([1, 2, 3, 1])
        with pytest.raises(TypeError):
            chromosome_array.equality_mask("1")

        with pytest.raises(TypeError):
            chromosome_array.equality_mask(True)

        with pytest.raises(TypeError):
            chromosome_array.equality_mask(0.1)

        mask = chromosome_array.equality_mask(None)
        expected_mask = None
        assert mask is expected_mask

        mask = chromosome_array.equality_mask(1)
        expected_mask = [True, False, False, True]
        assert np.array_equal(expected_mask, mask)

        snp_array = Dataset(["rs1", "rs1", "rs2", "rs3"])
        mask = snp_array.equality_mask("rs1")
        expected_mask = [True, True, False, False]
        assert np.array_equal(expected_mask, mask)

    def filter_by_mask(self):
        mask = [True, False, False, True]
        masked_vector = vector_int.filter_by_mask(mask)
        assert len(masked_vector) == 2
        assert masked_vector[0] == 1
        assert masked_vector[1] == 4

        vector = Dataset(["a", "b", "c", "d"])
        masked_vector = vector.filter_by_mask(mask)
        assert len(masked_vector) == 2
        assert masked_vector[0] == "a"
        assert masked_vector[1] == "d"
