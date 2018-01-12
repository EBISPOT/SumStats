import os

import h5py
import numpy as np
import pytest
import sumstats.utils.group as gu
import sumstats.utils.utils as utils
from sumstats.utils.dataset import Dataset


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
            gu._create_dset_placeholder(placeholder_size, value)

    def test_create_dset_placeholder_creates_dataset_of_size_and_value(self):
        placeholder_size = 5
        value = 1
        placeholder = gu._create_dset_placeholder(placeholder_size, value)
        assert len(placeholder) == 5
        assert len(set(placeholder)) == 1
        assert isinstance(placeholder, Dataset)

    def test_extend_dsets_for_group_extends_dictionary_with_array(self):
        self.group.create_dataset(simple_dset_name, data=simple_dset)

        new_dset = gu.create_dataset_from_value(dataset_with_same_values[0], size)
        print(new_dset)
        print(dataset_with_same_values)
        assert np.array_equal(new_dset, dataset_with_same_values)
