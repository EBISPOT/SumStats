import os

import numpy as np
import pytest
import sumstats.utils.group as gu
import sumstats.utils.utils as utils
from sumstats.utils.dataset import Dataset
from sumstats.common_constants import *


start = 0
size = 20
simple_dset = [1, 2, 3]
simple_dset_name = CHR_DSET
not_saved_dset_name = MANTISSA_DSET
non_existing_data = 5
dataset_with_same_values = ["a", "a", "a"]


class TestUnitGroup(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")
        self.file_group = gu.Group(self.f)
        self.file_group.create_subgroup("1")
        self.group_1 = self.file_group.get_subgroup("1")
        self.file_group.create_subgroup("1/sub1")
        s1 = self.group_1.get_subgroup("sub1")
        s1.generate_dataset(STUDY_DSET, ["study1"])
        self.file_group.create_subgroup("1/sub2")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_initializing_group_with_dataset_raises_error(self):
        dataset = self.file_group.generate_dataset(STUDY_DSET, ["study"])
        with pytest.raises(TypeError):
            gu.Group(dataset)

    def test_get_subgroup(self):
        group = self.file_group.get_subgroup(1)
        assert group.get_name() == "/1"

    def test_get_subgroup_raises_error_if_not_group(self):
        group = self.file_group.get_subgroup(1).get_subgroup("sub1")
        with pytest.raises(TypeError):
            group.get_subgroup(STUDY_DSET)

    def test_get_subgroup_raises_error_if_subgroup_doesnt_exist(self):
        group = self.file_group.get_subgroup(1).get_subgroup("sub1")
        with pytest.raises(ValueError):
            group.get_subgroup("sub12")

    def test_get_all_subgroups(self):
        group1 = self.file_group.get_subgroup(1)
        groups = group1.get_all_subgroups()
        assert len(groups) == 2
        assert isinstance(groups[0], gu.Group)

    def test_get_all_subgroups_returns_empty_when_parent_group_only_has_datasets(self):
        group = self.file_group.get_subgroup(1).get_subgroup("sub1")
        groups = group.get_all_subgroups()
        assert len(groups) == 0

    def test_get_all_subgroups_returns_only_groups_and_no_dsets(self):
        group = self.file_group.get_subgroup(1).get_subgroup("sub1")
        group.create_subgroup("sub11")
        groups = group.get_all_subgroups()
        assert len(groups) == 1
        assert "sub11" in groups[0].get_name()

    def test_generate_dataset_single_data_element(self):
        self.file_group.create_subgroup("random_group")
        random_group = self.file_group.get_subgroup("random_group")

        data = 1
        dset_name = BP_DSET
        random_group.generate_dataset(dset_name, [data])
        dset = random_group.get_dset(dset_name, start, size)
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == data

    def test_generate_dataset_raises_error_with_unknown_dset_name(self):
        self.file_group.create_subgroup("random_group")
        random_group = self.file_group.get_subgroup("random_group")

        data = 1
        dset_name = "random name"
        with pytest.raises(KeyError):
            random_group.generate_dataset(dset_name, [data])

    def test_expand_dataset_single_element(self):
        self.file_group.create_subgroup("random_group")
        random_group = self.file_group.get_subgroup("random_group")

        data = 'string1'
        dset_name = STUDY_DSET
        random_group.generate_dataset(dset_name, [data])
        data2 = 'random string4'
        random_group.expand_dataset(dset_name, [data2])

        dset = random_group.get_dset(dset_name, start, size)
        assert len(dset) == 2
        dataset = dset[:]
        assert dataset[0] == 'string1'
        assert dataset[1] == 'random string4'

    def test_expand_not_existing_dataset(self):
        self.file_group.create_subgroup("random_group")
        random_group = self.file_group.get_subgroup("random_group")

        data = 'string1'
        dset_name = STUDY_DSET
        random_group.expand_dataset(dset_name, [data])
        dset = random_group.get_dset(dset_name, start, size)

        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == 'string1'

    def test_generate_dataset_list_of_elements(self):
        self.file_group.create_subgroup("random_group")
        random_group = self.file_group.get_subgroup("random_group")

        data = ['string 1', 'str2']
        dset_name = STUDY_DSET
        random_group.generate_dataset(dset_name, data)
        dset = random_group.get_dset(dset_name, start, size)
        dataset = dset[:]
        assert len(dataset) == 2
        assert dataset[0] == data[0]
        assert dataset[1] == data[1]

    def test_expand_dataset_list_of_elements(self):
        self.file_group.create_subgroup("random_group")
        random_group = self.file_group.get_subgroup("random_group")

        data = ['string1', 'str2']
        dset_name = STUDY_DSET
        random_group.generate_dataset(dset_name, data)
        data2 = ['string3', 'random string']
        random_group.expand_dataset(dset_name, data2)

        dataset = random_group.get_dset(dset_name, start, size)
        assert len(dataset) != 0
        assert len(dataset) == 4
        dset_data = dataset[:]
        assert dset_data[0] == data[0]
        assert dset_data[1] == data[1]
        assert dset_data[2] == data2[0]
        assert dset_data[3] == data2[1]

    def test_get_dset(self):
        self.group_1.generate_dataset(simple_dset_name, data=simple_dset)
        dataset = self.group_1.get_dset(simple_dset_name, start, size)
        assert np.array_equal(dataset, simple_dset)

    def test_get_non_existing_dset_returns_none(self):
        dataset = self.group_1.get_dset(not_saved_dset_name, start, size)
        assert len(dataset) == 0

    def test_check_group_dsets_shape(self):
        self.file_group.create_subgroup("/rs185339560")
        group = self.file_group.get_subgroup("/rs185339560")
        study_dset = np.array(['study1'], dtype=h5py.special_dtype(vlen=str))
        mantissa_dset = np.array([0.1, 0.2], dtype=float)

        group.generate_dataset('study', study_dset)
        group.generate_dataset('mantissa', mantissa_dset)
        TO_STORE_DSETS = ['study', 'mantissa']

        with pytest.raises(AssertionError):
            group.check_datasets_consistent(TO_STORE_DSETS)

    def test_check_group_dsets_shape_one_dset_empty(self):
        self.file_group.create_subgroup("/rs185339560")
        group = self.file_group.get_subgroup("rs185339560")
        study_dset = np.array(['study1'], dtype=h5py.special_dtype(vlen=str))

        group.generate_dataset('study', study_dset)
        TO_STORE_DSETS = ['study', 'mantissa']

        with pytest.raises(AssertionError):
            group.check_datasets_consistent(TO_STORE_DSETS)

    def test_check_group_dsets_shape_first_load(self):
        self.file_group.create_subgroup("/rs185339560")
        group = self.file_group.get_subgroup("/rs185339560")
        TO_STORE_DSETS = ['study', 'mantissa']
        group.check_datasets_consistent(TO_STORE_DSETS)

    def test_check_group_dsets_shape_all_ok(self):
        self.file_group.create_subgroup("/rs185339560")
        group = self.file_group.get_subgroup("rs185339560")
        study_dset = np.array(['study1', 'study2'], dtype=h5py.special_dtype(vlen=str))
        mantissa_dset = np.array([0.1, 0.2], dtype=float)

        group.generate_dataset('study', study_dset)
        group.generate_dataset('mantissa', mantissa_dset)
        TO_STORE_DSETS = ['study', 'mantissa']

        group.check_datasets_consistent(TO_STORE_DSETS)

    def test_already_loaded_returns_true_for_loaded_data(self):
        self.group_1.generate_dataset(simple_dset_name, simple_dset)
        assert self.group_1.is_value_in_dataset(simple_dset[0], simple_dset_name)

    def test_already_loaded_returns_false_for_data_non_existing_data(self):
        assert not self.group_1.is_value_in_dataset(non_existing_data, simple_dset_name)

    def test_already_loaded_returns_false_for_non_existing_dataset_name(self):
        assert not self.group_1.is_value_in_dataset(simple_dset[0], not_saved_dset_name)

    def test_get_non_existing_dset_from_group_returns_empty_array(self):
        snp_group = self.group_1.get_dset(not_saved_dset_name, start, size)
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
        self.group_1.generate_dataset(REFERENCE_DSET, data=simple_dset)
        new_dset = self.group_1.create_dataset_from_value(dataset_with_same_values[0], start, size)

        assert np.array_equal(new_dset, dataset_with_same_values)