import os
import h5py
import numpy as np
import pytest
from sumstats.utils.restrictions import *
import sumstats.utils.utils as utils
from sumstats.utils.dataset import Dataset


class TestQueryUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_filter_dictionary_by_mask(self):
        dict = {'dset1': Dataset([1, 2, 3]), 'dset2': Dataset([1, 3, 3])}
        pvals = Dataset([1, 2, 2])
        mask = pvals.equality_mask(1)
        print(mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        for dset in dict:
            assert np.array_equal(dict[dset], [1])

        dict = {'dset1': Dataset(["a", "b", "c"]), 'dset2': Dataset(["c", "d", "e"])}
        pvals = Dataset([1, 2, 2])
        mask = pvals.equality_mask(1)
        print(mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        assert np.array_equal(dict["dset1"], ["a"])
        assert np.array_equal(dict["dset2"], ["c"])

        dict = {'dset1': Dataset(["a", "b", "c"]), 'dset2': Dataset(["c", "d", "e"])}
        pvals = Dataset([1, 2, 2])
        mask = pvals.equality_mask(2, )
        print(mask)
        dict = utils.filter_dictionary_by_mask(dict, mask)
        assert np.array_equal(dict["dset1"], ["b", "c"])
        assert np.array_equal(dict["dset2"], ["d", "e"])

    def test_filter_dsets_with_restrictions(self):
        name_to_dataset = {'snp': Dataset(["rs1", "rs1", "rs1", "rs2", "rs3"]), 'pval': Dataset([1., 2.1, 3, 3.1, 4]),
                           'chr': Dataset([1, 1, 1, 1, 2])}

        restrictions = [EqualityRestriction("rs1", name_to_dataset["snp"]),
                        IntervalRestriction(1., 2.1, name_to_dataset["pval"]),
                        EqualityRestriction(1, name_to_dataset["chr"])]

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)

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

        restrictions = [IntervalRestriction(3., 3.1, name_to_dataset["pval"]),
                        EqualityRestriction(1, name_to_dataset["chr"])]

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
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

        restrictions = [IntervalRestriction(4., 4., name_to_dataset["pval"]), ]

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(list(filtered_dsets.keys())) == 3
        assert len(filtered_dsets['snp']) == 1

        assert filtered_dsets['snp'][0] == "rs3"

        assert len(filtered_dsets['pval']) == 1
        assert filtered_dsets['pval'][0] == 4.

        assert len(filtered_dsets['chr']) == 1
        assert filtered_dsets['chr'][0] == 2

        #
        restrictions = []

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(list(filtered_dsets.keys())) == 3
        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 5

    def test_evaluate_datasets(self):
        name_to_dataset = {}
        utils.assert_datasets_not_empty(name_to_dataset)

        name_to_dataset = {'snp': ["rs1", "rs2", "rs3"], 'pval': [0.1, 3.1, 2.1],
                           'chr': [1, 2, 3]}
        utils.assert_datasets_not_empty(name_to_dataset)

        name_to_dataset = {'snp': None}
        with pytest.raises(ValueError):
            utils.assert_datasets_not_empty(name_to_dataset)

        name_to_dataset = {'snp': []}
        with pytest.raises(ValueError):
            utils.assert_datasets_not_empty(name_to_dataset)

    def test_empty_array(self):
        assert utils.empty_array(None)
        assert utils.empty_array([])
        assert not utils.empty_array("not an array")
        assert not utils.empty_array([1, 2, 3])
        assert not utils.empty_array(Dataset([1, 2, 3]))

    def test_get_mantissa_and_exp_lists(self):
        list_of_strings = ['1.2', '0.1', '0.0', '0.002', '0.8e-10', '8E-10']
        mantissa_list, exp_list = utils.get_mantissa_and_exp_lists(list_of_strings)

        assert mantissa_list is not None
        assert len(mantissa_list) == len(list_of_strings)
        assert np.array_equal(mantissa_list, [1.2, 1., 0., 2., 0.8, 8.])

        assert exp_list is not None
        assert len(exp_list) == len(list_of_strings)
        assert np.array_equal(exp_list, [0, -1, 0, -3, -10, -10])

        list_of_strings = ['1,2']
        with pytest.raises(ValueError):
            utils.get_mantissa_and_exp_lists(list_of_strings)

        list_of_strings = [1.2]
        with pytest.raises(TypeError):
            utils.get_mantissa_and_exp_lists(list_of_strings)

        list_of_strings = [1]
        with pytest.raises(TypeError):
            utils.get_mantissa_and_exp_lists(list_of_strings)

    def test_create_dataset_objects(self):
        name_to_dsets = {'dset1' : [1, 2, 3], 'dset2' : ['1,' '2', '3'], 'dset3' : [1., 2., 3.]}
        name_to_dsets = utils.create_datasets_from_lists(name_to_dsets)
        for name, dataset in name_to_dsets.items():
            assert isinstance(dataset, Dataset)

    def test_create_dictionary_of_empty_dsets(self):
        name_to_dsets = utils.create_dictionary_of_empty_dsets(['dset1', 'dset2'])

        assert len(name_to_dsets) == 2

        assert isinstance(name_to_dsets['dset1'], Dataset)
        assert len(name_to_dsets['dset1']) == 0

        assert isinstance(name_to_dsets['dset2'], Dataset)
        assert len(name_to_dsets['dset2']) == 0