import os

import h5py
import numpy as np
import pytest
import sumstats.utils.utils as utils


class TestQueryUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_group_from_parent(self):
        self.f.create_group("1")
        group = utils.get_group_from_parent(self.f, 1)
        assert group.name == "/1"

        group = utils.get_group_from_parent(self.f, "1")
        assert group.name == "/1"

        with pytest.raises(ValueError):
            utils.get_group_from_parent(self.f, "23")

        group.create_group("subgroup")
        subgroup = utils.get_group_from_parent(group, "subgroup")
        assert subgroup.name == "/1/subgroup"

        with pytest.raises(ValueError):
            utils.get_group_from_parent(group, "subgroup1")

        with pytest.raises(ValueError):
            utils.get_group_from_parent(self.f, "subgroup")

    def test_get_dset(self):
        group = self.f.create_group("1")
        data = np.array([1, 2, 3])
        group.create_dataset("dset", data=data)

        dataset = utils.get_dset(group, "dset")
        assert np.array_equal(dataset, data)

        dataset = utils.get_dset(group, "dset1")
        assert dataset is None

    def test_get_upper_limit_mask(self):
        vector = np.array([1, 2, 3, 4])
        upper_limit = 3
        expected_mask = [True, True, True, False]
        mask = utils.get_upper_limit_mask(upper_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = np.array(["1", "2", "3", "4"])
        upper_limit = "2"
        expected_mask = [True, True, False, False]
        mask = utils.get_upper_limit_mask(upper_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = np.array(["1", "2", "3", "4"])
        upper_limit = 2
        with pytest.raises(TypeError):
            utils.get_upper_limit_mask(upper_limit, vector)

    def test_get_lower_limit_mask(self):
        vector = np.array([1, 2, 3, 4])
        lower_limit = 3
        expected_mask = [False, False, True, True]
        mask = utils.get_lower_limit_mask(lower_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = np.array(["1", "2", "3", "4"])
        lower_limit = "2"
        expected_mask = [False, True, True, True]
        mask = utils.get_lower_limit_mask(lower_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = np.array(["1", "2", "3", "4"])
        lower_limit = 2
        with pytest.raises(TypeError):
            utils.get_lower_limit_mask(lower_limit, vector)

    def test_combine_masks(self):
        mask1 = [True, True]
        mask2 = [True, False]
        expected_mask = [True, False]
        mask = utils.combine_masks(mask1, mask2)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = [True, False, True]
        expected_mask = [True, False]
        mask = utils.combine_masks(mask1, mask2)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = [True, False, False]
        expected_mask = [True, False]
        mask = utils.combine_masks(mask1, mask2)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = None
        expected_mask = mask1
        mask = utils.combine_masks(mask1, mask2)
        assert np.array_equal(expected_mask, mask)

        mask1 = None
        mask2 = [True, True]
        expected_mask = mask2
        mask = utils.combine_masks(mask1, mask2)
        assert np.array_equal(expected_mask, mask)

        mask1 = None
        mask2 = None
        expected_mask = None
        mask = utils.combine_masks(mask1, mask2)
        assert np.array_equal(expected_mask, mask)

    def test_get_cutoff_mask(self):
        block_floor = 0
        block_ceil = block_size = 100000
        bp_chr_array = np.asarray([0, 100000, 100001, 1, 50000, 200000])
        expected_mask = [True, True, False, True, True, False]
        block_mask = utils.cutoff_mask(bp_chr_array, block_floor, block_ceil)
        assert np.array_equal(expected_mask, block_mask)

        block_floor = block_ceil + 1
        block_ceil += block_size
        bp_chr_array = np.asarray([0, 100000, 100001, 1, 50000, 200000, 200001, 300000])
        expected_mask = [False, False, True, False, False, True, False, False]
        block_mask = utils.cutoff_mask(bp_chr_array, block_floor, block_ceil)
        assert np.array_equal(expected_mask, block_mask)

        with pytest.raises(TypeError):
            utils.cutoff_mask(bp_chr_array, "a", block_ceil)

        with pytest.raises(TypeError):
            utils.cutoff_mask(bp_chr_array, True, block_ceil)

        with pytest.raises(TypeError):
            utils.cutoff_mask(bp_chr_array, 0.1, block_ceil)

        with pytest.raises(TypeError):
            utils.cutoff_mask(bp_chr_array, 0.1, 0.3)

        with pytest.raises(TypeError):
            utils.cutoff_mask(bp_chr_array, block_floor, "a")

        with pytest.raises(TypeError):
            utils.cutoff_mask(bp_chr_array, block_floor, False)

        with pytest.raises(TypeError):
            bp_chr_array = np.array(["a", "b", "c", "d", "d", "d", "d", "d"])
            utils.cutoff_mask(bp_chr_array, block_floor, block_ceil)

    def test_get_equality_mask(self):
        chromosome_array = np.asarray([1, 2, 3, 1])
        with pytest.raises(TypeError):
            utils.get_equality_mask("1", chromosome_array)

        with pytest.raises(TypeError):
            utils.get_equality_mask(True, chromosome_array)

        with pytest.raises(TypeError):
            utils.get_equality_mask(0.1, chromosome_array)

        mask = utils.get_equality_mask(None, chromosome_array)
        expected_mask = None
        assert mask is expected_mask

        mask = utils.get_equality_mask(1, chromosome_array)
        expected_mask = [True, False, False, True]
        assert np.array_equal(expected_mask, mask)

        snp_array = np.asarray(["rs1", "rs1", "rs2", "rs3"])
        mask = utils.get_equality_mask("rs1", snp_array)
        expected_mask = [True, True, False, False]
        assert np.array_equal(expected_mask, mask)

    def test_filter_by_mask(self):
        vector = np.asarray([1, 2, 3, 4])
        mask = [True, False, False, True]
        masked_vector = utils.filter_by_mask(vector, mask)
        assert len(masked_vector) == 2
        assert masked_vector[0] == 1
        assert masked_vector[1] == 4

        vector = np.asarray(["a", "b", "c", "d"])
        masked_vector = utils.filter_by_mask(vector, mask)
        assert len(masked_vector) == 2
        assert masked_vector[0] == "a"
        assert masked_vector[1] == "d"

        mask = [1, 3, True, False]
        with pytest.raises(TypeError):
            utils.filter_by_mask(vector, mask)

        mask = ["a", "a", "a", "b"]
        with pytest.raises(TypeError):
            utils.filter_by_mask(vector, mask)

        mask = [1, 1, 1, 0]
        with pytest.raises(TypeError):
            utils.filter_by_mask(vector, mask)

        mask = [1.4, 1.3, 1.2, 0.1]
        with pytest.raises(TypeError):
            utils.filter_by_mask(vector, mask)

    def test_filter_dictionary_by_mask(self):
        dict = {'dset1' : np.array([1, 2, 3]), 'dset2' : np.array([1, 3, 3])}
        pvals = np.array([1, 2, 2])
        mask = utils.get_equality_mask(1, pvals)
        print (mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        for dset in dict:
            assert np.array_equal(dict[dset], np.array([1]))

        dict = {'dset1' : np.array(["a", "b", "c"]), 'dset2' : np.array(["c", "d", "e"])}
        pvals = np.array([1, 2, 2])
        mask = utils.get_equality_mask(1, pvals)
        print (mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        assert np.array_equal(dict["dset1"], np.array(["a"]))
        assert np.array_equal(dict["dset2"], np.array(["c"]))

        dict = {'dset1' : np.array(["a", "b", "c"]), 'dset2' : np.array(["c", "d", "e"])}
        pvals = np.array([1, 2, 2])
        mask = utils.get_equality_mask(2, pvals)
        print (mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        assert np.array_equal(dict["dset1"], np.array(["b", "c"]))
        assert np.array_equal(dict["dset2"], np.array(["d", "e"]))

    def test_convert_lists_to_np_arrays(self):
        vlen_dtype = h5py.special_dtype(vlen=str)
        DSET_TYPES = {'snp': vlen_dtype, 'pval': float, 'study': vlen_dtype, 'chr': int, 'or': float, 'bp': int,
                      'effect': vlen_dtype, 'other': vlen_dtype}

        dict_of_dsets = {'snp': [1, 2, 3], 'pval': ["1", "2", "3"], 'chr': ["1", "2", "3"]}

        dict_of_dsets = utils.convert_lists_to_np_arrays(dict_of_dsets, DSET_TYPES)
        assert dict_of_dsets['snp'].dtype == vlen_dtype
        assert dict_of_dsets['pval'].dtype == float
        assert dict_of_dsets['chr'].dtype == int

        dict_of_dsets['bp'] = []
        dict_of_dsets = utils.convert_lists_to_np_arrays(dict_of_dsets, DSET_TYPES)
        assert len(dict_of_dsets['bp']) == 0

        dict_of_dsets['random'] = [1, 2, 3]
        with pytest.raises(KeyError):
            utils.convert_lists_to_np_arrays(dict_of_dsets, DSET_TYPES)

    def test_remove_headers(self):
        TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr' ]
        dict_of_dsets = {'snp': ["snp", "rs1", "rs2", "rs3"], 'pval': ["pval", 1, 3.1, 2.1], 'chr': ["chr", 1, 2, 3]}

        dict_of_dsets = utils.remove_headers(dict_of_dsets, TO_LOAD_DSET_HEADERS)
        assert "snp" not in dict_of_dsets['snp']
        assert "pval" not in dict_of_dsets['pval']
        assert "chr" not in dict_of_dsets['chr']

        TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr']
        dict_of_dsets = {'snp': ['study', 1, 2, 3], 'pval': ['pval', "1", "2", "3"], 'chr': ['chr', "1", "2", "3"]}
        with pytest.raises(ValueError):
            utils.remove_headers(dict_of_dsets, TO_LOAD_DSET_HEADERS)

        TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr']
        dict_of_dsets = {'snp': [1, 2, 3], 'pval': ['pval', "1", "2", "3"], 'chr': ['chr', "1", "2", "3"]}
        with pytest.raises(ValueError):
            utils.remove_headers(dict_of_dsets, TO_LOAD_DSET_HEADERS)

        TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr', 'or']
        dict_of_dsets = {'snp': ["snp", "rs1", "rs2", "rs3"], 'pval': ["pval", 1, 3.1, 2.1], 'chr': ["chr", 1, 2, 3]}
        with pytest.raises(KeyError):
            utils.remove_headers(dict_of_dsets, TO_LOAD_DSET_HEADERS)

    def test_evaluate_datasets(self):
        print()
        dict_of_dsets = {}
        utils.evaluate_np_datasets(dict_of_dsets)

        dict_of_dsets = {'snp': ["rs1", "rs2", "rs3"], 'pval': [0.1, 3.1, 2.1], 'chr': [1, 2, 3]}
        with pytest.raises(AttributeError):
            utils.evaluate_np_datasets(dict_of_dsets)

        dict_of_dsets = {'snp': np.array(["rs1", "rs2", "rs3"]), 'pval': np.array([0.1, 3.1, 2.1]), 'chr': np.array([1, 2, 3])}
        utils.evaluate_np_datasets(dict_of_dsets)

        dict_of_dsets = {'snp': np.array(None)}
        with pytest.raises(ValueError):
            utils.evaluate_np_datasets(dict_of_dsets)

        dict_of_dsets = {'snp': np.array([])}
        with pytest.raises(ValueError):
            utils.evaluate_np_datasets(dict_of_dsets)



