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
        self.group.create_dataset(simple_dset_name, data=simple_dset)

    def teardown_method(self, method):
        os.remove(self.h5file)

    def get_group_from_parent(self):
        group = gu.get_group_from_parent(self.f, 1)
        assert group.name == "/1"

    def get_non_existing_group_from_parent_raises_error(self):
        with pytest.raises(ValueError):
            gu.get_group_from_parent(self.f, "23")

    def get_all_groups_from_parent(self):
        group1 = gu.get_group_from_parent(self.f, 1)
        groups = gu.get_all_groups_from_parent(group1)
        assert len(groups) == 2
        assert isinstance(groups[0], h5py._hl.group.Group)

    def get_dset(self):
        dataset = gu.get_dset(self.group, simple_dset_name, start, size)
        assert np.array_equal(dataset, simple_dset)

    def get_non_existing_dset_returns_none(self):
        dataset = gu.get_dset(self.group, not_saved_dset_name, start, size)
        assert dataset is None

    def check_group_dsets_shape(self):
        group = self.f.create_group("/rs185339560")
        study_dset = np.array(['study1'], dtype=h5py.special_dtype(vlen=str))
        mantissa_dset = np.array([0.1, 0.2], dtype=float)

        group.create_dataset(name='study', data=study_dset, maxshape=(None,))
        group.create_dataset(name='mantissa', data=mantissa_dset, maxshape=(None,))
        TO_STORE_DSETS = ['study', 'mantissa']

        with pytest.raises(AssertionError):
            gu.check_group_dsets_shape(group, TO_STORE_DSETS)

    def check_group_dsets_shape_one_dset_empty(self):
        group = self.f.create_group("/rs185339560")
        study_dset = np.array(['study1'], dtype=h5py.special_dtype(vlen=str))

        group.create_dataset(name='study', data=study_dset, maxshape=(None,))
        TO_STORE_DSETS = ['study', 'mantissa']

        with pytest.raises(AssertionError):
            gu.check_group_dsets_shape(group, TO_STORE_DSETS)

    def check_group_dsets_shape_first_load(self):
        group = self.f.create_group("/rs185339560")
        TO_STORE_DSETS = ['study', 'mantissa']
        gu.check_group_dsets_shape(group, TO_STORE_DSETS)

    def check_group_dsets_shape_all_ok(self):
        group = self.f.create_group("/rs185339560")
        study_dset = np.array(['study1', 'study2'], dtype=h5py.special_dtype(vlen=str))
        mantissa_dset = np.array([0.1, 0.2], dtype=float)

        group.create_dataset(name='study', data=study_dset, maxshape=(None,))
        group.create_dataset(name='mantissa', data=mantissa_dset, maxshape=(None,))
        TO_STORE_DSETS = ['study', 'mantissa']

        gu.check_group_dsets_shape(group, TO_STORE_DSETS)

    def already_loaded_returns_true_for_loaded_data(self):
        assert gu.already_loaded_in_group(self.group, simple_dset[0], simple_dset_name)

    def already_loaded_returns_false_for_data_non_existing_data(self):
        assert not gu.already_loaded_in_group(self.group, non_existing_data, simple_dset_name)

    def already_loaded_returns_false_for_non_existing_dataset_name(self):
        assert not gu.already_loaded_in_group(self.group, simple_dset[0], not_saved_dset_name)

    def get_non_existing_dset_from_group_returns_empty_array(self):
        snp_group = gu._get_dset_from_group(not_saved_dset_name, self.group, start, size)
        assert utils.empty_array(snp_group)

    def create_dset_placeholder_raises_error_for_none_value(self):
        size = 5
        value = None
        with pytest.raises(AssertionError):
            gu._create_dset_placeholder(size, value)

    def create_dset_placeholder_creates_dataset_of_size_and_value(self):
        value = 1
        placeholder = gu._create_dset_placeholder(size, value)
        assert len(placeholder) == 5
        assert len(set(placeholder)) == 1
        assert isinstance(placeholder, Dataset)

    def extend_dsets_for_group_doesnt_change_other_arrays_in_dictionary(self):
        new_dset_name = 'dset_new'
        TO_QUERY = [simple_dset_name, new_dset_name]
        name_to_dset = utils.create_dictionary_of_empty_dsets(TO_QUERY)
        name_to_dset = gu.extend_dsets_for_group_missing(missing_value=dataset_with_same_values[0], group=self.group,
                                                         name_to_dataset=name_to_dset,
                                                         missing_dset=new_dset_name, start=start, size=size)

        assert np.array_equal(name_to_dset[simple_dset_name], simple_dset)


    def extend_dsets_for_group_extends_dictionary_with_array(self):
        new_dset_name = 'dset_new'
        TO_QUERY = [simple_dset_name, new_dset_name]
        name_to_dset = utils.create_dictionary_of_empty_dsets(TO_QUERY)
        name_to_dset = gu.extend_dsets_for_group_missing(missing_value=dataset_with_same_values[0], group=self.group,
                                                         name_to_dataset=name_to_dset,
                                                         missing_dset=new_dset_name, start=start, size=size)

        assert np.array_equal(name_to_dset[new_dset_name], dataset_with_same_values)
