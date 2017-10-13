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
        vector = [1, 2, 3, 4]
        upper_limit = 3
        expected_mask = [True, True, True, False]
        mask = utils.get_upper_limit_mask(upper_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = ["1", "2", "3", "4"]
        upper_limit = "2"
        expected_mask = [True, True, False, False]
        mask = utils.get_upper_limit_mask(upper_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = ["1", "2", "3", "4"]
        upper_limit = 2
        with pytest.raises(TypeError):
            utils.get_upper_limit_mask(upper_limit, vector)

    def test_get_lower_limit_mask(self):
        vector = [1, 2, 3, 4]
        lower_limit = 3
        expected_mask = [False, False, True, True]
        mask = utils.get_lower_limit_mask(lower_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = ["1", "2", "3", "4"]
        lower_limit = "2"
        expected_mask = [False, True, True, True]
        mask = utils.get_lower_limit_mask(lower_limit, vector)
        assert np.array_equal(expected_mask, mask)

        vector = ["1", "2", "3", "4"]
        lower_limit = 2
        with pytest.raises(TypeError):
            utils.get_lower_limit_mask(lower_limit, vector)

    def test_combine_list_of_masks(self):
        mask1 = [True, True]
        mask2 = [True, False]
        expected_mask = [True, False]
        list_of_masks = [mask1, mask2]
        mask = utils.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = [True, False, True]
        expected_mask = [True, False]
        list_of_masks = [mask1, mask2]
        mask = utils.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = [True, False, False]
        expected_mask = [True, False]
        list_of_masks = [mask1, mask2]
        mask = utils.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = [True, True]
        mask2 = None
        expected_mask = mask1
        list_of_masks = [mask1, mask2]
        mask = utils.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = None
        mask2 = [True, True]
        expected_mask = mask2
        list_of_masks = [mask1, mask2]
        mask = utils.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

        mask1 = None
        mask2 = None
        expected_mask = None
        list_of_masks = [mask1, mask2]
        mask = utils.combine_list_of_masks(list_of_masks)
        assert np.array_equal(expected_mask, mask)

    def test_get_cutoff_mask(self):
        block_floor = 0
        block_ceil = block_size = 100000
        bp_chr_array = np.asarray([0, 100000, 100001, 1, 50000, 200000])
        expected_mask = [True, True, False, True, True, False]
        block_mask = utils.interval_mask(block_floor, block_ceil, bp_chr_array)
        assert np.array_equal(expected_mask, block_mask)

        block_floor = block_ceil + 1
        block_ceil += block_size
        bp_chr_array = np.asarray([0, 100000, 100001, 1, 50000, 200000, 200001, 300000])
        expected_mask = [False, False, True, False, False, True, False, False]
        block_mask = utils.interval_mask(block_floor, block_ceil, bp_chr_array)
        assert np.array_equal(expected_mask, block_mask)

        with pytest.raises(TypeError):
            utils.interval_mask("a", block_ceil, bp_chr_array)

        with pytest.raises(TypeError):
            utils.interval_mask(True, block_ceil, bp_chr_array)

        with pytest.raises(TypeError):
            utils.interval_mask(0.1, block_ceil, bp_chr_array)

        with pytest.raises(TypeError):
            utils.interval_mask(0.1, 0.3, bp_chr_array)

        with pytest.raises(TypeError):
            utils.interval_mask(block_floor, "a", bp_chr_array)

        with pytest.raises(TypeError):
            utils.interval_mask(block_floor, False, bp_chr_array)

        with pytest.raises(TypeError):
            bp_chr_array = ["a", "b", "c", "d", "d", "d", "d", "d"]
            utils.interval_mask(block_floor, block_ceil, bp_chr_array)

    def test_get_equality_mask(self):
        chromosome_array = np.asarray([1, 2, 3, 1])
        with pytest.raises(TypeError):
            utils.equality_mask("1", chromosome_array)

        with pytest.raises(TypeError):
            utils.equality_mask(True, chromosome_array)

        with pytest.raises(TypeError):
            utils.equality_mask(0.1, chromosome_array)

        mask = utils.equality_mask(None, chromosome_array)
        expected_mask = None
        assert mask is expected_mask

        mask = utils.equality_mask(1, chromosome_array)
        expected_mask = [True, False, False, True]
        assert np.array_equal(expected_mask, mask)

        snp_array = np.asarray(["rs1", "rs1", "rs2", "rs3"])
        mask = utils.equality_mask("rs1", snp_array)
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

    def test_filter_dictionary_by_mask(self):
        dict = {'dset1' : [1, 2, 3], 'dset2' : [1, 3, 3]}
        pvals = [1, 2, 2]
        mask = utils.equality_mask(1, pvals)
        print (mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        for dset in dict:
            assert np.array_equal(dict[dset], [1])

        dict = {'dset1' : ["a", "b", "c"], 'dset2' : ["c", "d", "e"]}
        pvals = [1, 2, 2]
        mask = utils.equality_mask(1, pvals)
        print (mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        assert np.array_equal(dict["dset1"], ["a"])
        assert np.array_equal(dict["dset2"], ["c"])

        dict = {'dset1' : ["a", "b", "c"], 'dset2' : ["c", "d", "e"]}
        pvals = [1, 2, 2]
        mask = utils.equality_mask(2, pvals)
        print (mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        assert np.array_equal(dict["dset1"], ["b", "c"])
        assert np.array_equal(dict["dset2"], ["d", "e"])

    def test_filter_dsets_with_restrictions(self):
        name_to_dataset = {'snp': ["rs1", "rs1", "rs1", "rs2", "rs3"], 'pval': [1., 2.1, 3, 3.1, 4],
                               'chr': [1, 1, 1, 1, 2]}

        dset_names_to_restriction = {'snp' : "rs1", 'pval' : (1., 2.1), 'chr' : 1}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, dset_names_to_restriction)

        assert len(list(filtered_dsets.keys())) == 3

        assert len(filtered_dsets['snp']) == 2
        assert len(set(filtered_dsets['snp'])) == 1
        assert filtered_dsets['snp'][0] == "rs1"

        assert len(filtered_dsets['pval']) == 2
        for pval in filtered_dsets['pval']:
            assert pval >= 1.
            assert pval <= 2.1

        assert len(filtered_dsets['chr']) == 2
        for chr in filtered_dsets['chr']:
            assert chr == 1

        dset_names_to_restriction = {'pval': (3., 3.1), 'chr': 1}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, dset_names_to_restriction)
        assert len(list(filtered_dsets.keys())) == 3
        assert len(filtered_dsets['snp']) == 2

        assert filtered_dsets['snp'][0] == "rs1"
        assert filtered_dsets['snp'][1] == "rs2"

        assert len(filtered_dsets['pval']) == 2
        for pval in filtered_dsets['pval']:
            assert pval >= 3.
            assert pval <= 3.1

        assert len(filtered_dsets['chr']) == 2
        for chr in filtered_dsets['chr']:
            assert chr == 1

        dset_names_to_restriction = {'pval': (4., 4.)}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, dset_names_to_restriction)
        assert len(list(filtered_dsets.keys())) == 3
        assert len(filtered_dsets['snp']) == 1

        assert filtered_dsets['snp'][0] == "rs3"

        assert len(filtered_dsets['pval']) == 1
        assert filtered_dsets['pval'][0] == 4.

        assert len(filtered_dsets['chr']) == 1
        assert filtered_dsets['chr'][0] == 2


        #
        dset_names_to_restriction = {}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, dset_names_to_restriction)
        assert len(list(filtered_dsets.keys())) == 3
        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 5

    def test_convert_lists_to_np_arrays(self):
        vlen_dtype = h5py.special_dtype(vlen=str)
        DSET_TYPES = {'snp': vlen_dtype, 'pval': float, 'study': vlen_dtype, 'chr': int, 'or': float, 'bp': int,
                      'effect': vlen_dtype, 'other': vlen_dtype}

        name_to_dataset = {'snp': [1, 2, 3], 'pval': ["1", "2", "3"], 'chr': ["1", "2", "3"]}

        name_to_dataset = utils.convert_lists_to_np_arrays(name_to_dataset, DSET_TYPES)
        assert name_to_dataset['snp'].dtype == vlen_dtype
        assert name_to_dataset['pval'].dtype == float
        assert name_to_dataset['chr'].dtype == int

        name_to_dataset['bp'] = []
        name_to_dataset = utils.convert_lists_to_np_arrays(name_to_dataset, DSET_TYPES)
        assert len(name_to_dataset['bp']) == 0

        name_to_dataset['random'] = [1, 2, 3]
        with pytest.raises(KeyError):
            utils.convert_lists_to_np_arrays(name_to_dataset, DSET_TYPES)

    def test_remove_headers(self):
        TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr' ]
        name_to_dataset = {'snp': ["snp", "rs1", "rs2", "rs3"], 'pval': ["pval", 1, 3.1, 2.1], 'chr': ["chr", 1, 2, 3]}

        name_to_dataset = utils.remove_headers(name_to_dataset, TO_LOAD_DSET_HEADERS)
        assert "snp" not in name_to_dataset['snp']
        assert "pval" not in name_to_dataset['pval']
        assert "chr" not in name_to_dataset['chr']

        TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr']
        name_to_dataset = {'snp': ['study', 1, 2, 3], 'pval': ['pval', "1", "2", "3"], 'chr': ['chr', "1", "2", "3"]}
        with pytest.raises(ValueError):
            utils.remove_headers(name_to_dataset, TO_LOAD_DSET_HEADERS)

        TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr']
        name_to_dataset = {'snp': [1, 2, 3], 'pval': ['pval', "1", "2", "3"], 'chr': ['chr', "1", "2", "3"]}
        with pytest.raises(ValueError):
            utils.remove_headers(name_to_dataset, TO_LOAD_DSET_HEADERS)

        TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr', 'or']
        name_to_dataset = {'snp': ["snp", "rs1", "rs2", "rs3"], 'pval': ["pval", 1, 3.1, 2.1], 'chr': ["chr", 1, 2, 3]}
        with pytest.raises(KeyError):
            utils.remove_headers(name_to_dataset, TO_LOAD_DSET_HEADERS)

    def test_evaluate_datasets(self):
        print()
        name_to_dataset = {}
        utils.assert_np_datasets_not_empty(name_to_dataset)

        name_to_dataset = {'snp': ["rs1", "rs2", "rs3"], 'pval': [0.1, 3.1, 2.1], 'chr': [1, 2, 3]}
        with pytest.raises(AttributeError):
            utils.assert_np_datasets_not_empty(name_to_dataset)

        name_to_dataset = {'snp': np.array(["rs1", "rs2", "rs3"]), 'pval': np.array([0.1, 3.1, 2.1]), 'chr': np.array([1, 2, 3])}
        utils.assert_np_datasets_not_empty(name_to_dataset)

        name_to_dataset = {'snp': np.array(None)}
        with pytest.raises(ValueError):
            utils.assert_np_datasets_not_empty(name_to_dataset)

        name_to_dataset = {'snp': np.array([])}
        with pytest.raises(ValueError):
            utils.assert_np_datasets_not_empty(name_to_dataset)



