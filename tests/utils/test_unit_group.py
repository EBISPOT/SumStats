import os

import h5py
import numpy as np
import pytest
import sumstats.utils.group as gu
import sumstats.utils.utils as utils
from sumstats.utils.dataset import Dataset
from sumstats.common_constants import *


start = 0
size = 20
simple_dset = [1, 2, 3]
simple_dset_name = 'dset'
not_saved_dset_name = 'dset1'
non_existing_data = 5
dataset_with_same_values = ["a", "a", "a"]


class TestUnitGroup(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")
        self.group = self.f.create_group("1")
        self.f.create_group("1/sub1")
        self.f.create_group("1/sub2")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_group_from_parent(self):
        group = gu.create_group_from_parent(self.f, 1)
        assert group.name == "/1"

    def test_get_all_groups_from_parent(self):
        group1 = gu.create_group_from_parent(self.f, 1)
        groups = gu.get_all_subgroups(group1)
        print(groups)
        assert len(groups) == 2
        assert isinstance(groups[0], h5py._hl.group.Group)

    def test_create_dataset_single_data_element(self):
        random_group = self.f.create_group("random_group")

        data = 1
        dset_name = BP_DSET
        gu.create_dataset(random_group, dset_name, [data])
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == data

    def test_creat_dataset_raises_error_with_unknown_dset_name(self):
        random_group = self.f.create_group("random_group")

        data = 1
        dset_name = "random name"
        with pytest.raises(KeyError):
            gu.create_dataset(random_group, dset_name, [data])

    def test_expand_dataset_signle_element(self):
        random_group = self.f.create_group("random group")

        data = 'string1'
        dset_name = STUDY_DSET
        gu.create_dataset(random_group, dset_name, [data])
        data2 = 'random string4'
        gu.expand_dataset(random_group, dset_name, [data2])

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dataset = dset[:]
        assert dataset[0] == 'string1'
        assert dataset[1] == 'random string4'

    def test_expand_not_existing_dataset(self):
        random_group = self.f.create_group("random group")

        data = 'string1'
        dset_name = STUDY_DSET
        gu.expand_dataset(random_group, dset_name, [data])
        dset = random_group.get(dset_name)

        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == 'string1'

    def test_create_dataset_list_of_elements(self):
        random_group = self.f.create_group("random_group")
        data = ['string 1', 'str2']
        dset_name = STUDY_DSET
        gu.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 2
        assert dataset[0] == data[0]
        assert dataset[1] == data[1]

    def test_expand_dataset_list_of_elements(self):
        random_group = self.f.create_group("random group")

        data = ['string1', 'str2']
        dset_name = STUDY_DSET
        gu.create_dataset(random_group, dset_name, data)
        data2 = ['string3', 'random string']
        gu.expand_dataset(random_group, dset_name, data2)

        dataset = random_group.get(dset_name)
        assert dataset is not None
        assert len(dataset) == 4
        dset_data = dataset[:]
        assert dset_data[0] == data[0]
        assert dset_data[1] == data[1]
        assert dset_data[2] == data2[0]
        assert dset_data[3] == data2[1]

    def test_get_dset(self):
        self.group.create_dataset(simple_dset_name, data=simple_dset)
        dataset = gu.get_dset(self.group, simple_dset_name, start, size)
        assert np.array_equal(dataset, simple_dset)

    def test_get_non_existing_dset_returns_none(self):
        dataset = gu.get_dset(self.group, not_saved_dset_name, start, size)
        assert dataset is None

    def test_check_group_dsets_shape(self):
        group = self.f.create_group("/rs185339560")
        study_dset = np.array(['study1'], dtype=h5py.special_dtype(vlen=str))
        mantissa_dset = np.array([0.1, 0.2], dtype=float)

        group.create_dataset(name='study', data=study_dset, maxshape=(None,))
        group.create_dataset(name='mantissa', data=mantissa_dset, maxshape=(None,))
        TO_STORE_DSETS = ['study', 'mantissa']

        with pytest.raises(AssertionError):
            gu.check_group_dsets_shape(group, TO_STORE_DSETS)

    def test_check_group_dsets_shape_one_dset_empty(self):
        group = self.f.create_group("/rs185339560")
        study_dset = np.array(['study1'], dtype=h5py.special_dtype(vlen=str))

        group.create_dataset(name='study', data=study_dset, maxshape=(None,))
        TO_STORE_DSETS = ['study', 'mantissa']

        with pytest.raises(AssertionError):
            gu.check_group_dsets_shape(group, TO_STORE_DSETS)

    def test_check_group_dsets_shape_first_load(self):
        group = self.f.create_group("/rs185339560")
        TO_STORE_DSETS = ['study', 'mantissa']
        gu.check_group_dsets_shape(group, TO_STORE_DSETS)

    def test_check_group_dsets_shape_all_ok(self):
        group = self.f.create_group("/rs185339560")
        study_dset = np.array(['study1', 'study2'], dtype=h5py.special_dtype(vlen=str))
        mantissa_dset = np.array([0.1, 0.2], dtype=float)

        group.create_dataset(name='study', data=study_dset, maxshape=(None,))
        group.create_dataset(name='mantissa', data=mantissa_dset, maxshape=(None,))
        TO_STORE_DSETS = ['study', 'mantissa']

        gu.check_group_dsets_shape(group, TO_STORE_DSETS)

    def test_already_loaded_returns_true_for_loaded_data(self):
        self.group.create_dataset(simple_dset_name, data=simple_dset)
        assert gu.value_in_dataset(self.group, simple_dset[0], simple_dset_name)

    def test_already_loaded_returns_false_for_data_non_existing_data(self):
        assert not gu.value_in_dataset(self.group, non_existing_data, simple_dset_name)

    def test_already_loaded_returns_false_for_non_existing_dataset_name(self):
        assert not gu.value_in_dataset(self.group, simple_dset[0], not_saved_dset_name)

    def test_get_non_existing_dset_from_group_returns_empty_array(self):
        snp_group = gu._get_dset_from_group(not_saved_dset_name, self.group, start, size)
        assert utils.empty_array(snp_group)

    def test_create_dset_placeholder_raises_error_for_none_value(self):
        placeholder_size = 5
        value = None
        with pytest.raises(AssertionError):
            gu._create_dset_placeholder(value, placeholder_size)

    def test_create_dset_placeholder_creates_dataset_of_size_and_value(self):
        placeholder_size = 5
        value = 1
        placeholder = gu._create_dset_placeholder(value, placeholder_size)

        assert len(placeholder) == placeholder_size
        assert len(set(placeholder)) == value
        assert isinstance(placeholder, Dataset)

    def test_extend_dsets_for_group_extends_dictionary_with_array(self):
        self.group.create_dataset(REFERENCE_DSET, data=simple_dset)
        new_dset = gu.create_dataset_from_value(dataset_with_same_values[0], self.group, start, size)

        assert np.array_equal(new_dset, dataset_with_same_values)