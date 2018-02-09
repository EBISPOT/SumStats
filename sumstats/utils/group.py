"""
Utilities for hdf5 groups
"""

from sumstats.utils.dataset import Dataset
import numpy as np
from sumstats.common_constants import *


class Group:
    def __init__(self, group):
        # an actual HDF5 group
        if not (isinstance(group, h5py.Group) or isinstance(group, h5py.File)):
            raise TypeError("Trying to intialize Group object with something other than a hdf5 group or hdf5 file!")
        self.group = group

    def get_values(self):
        for dataset in self.group.values():
            if isinstance(dataset, h5py.Group):
                yield Group(dataset)
            else:
                yield dataset

    def get_items(self):
        for name, dataset in self.group.items():
            if isinstance(dataset, h5py.Group):
                yield (name, Group(dataset))
            else:
                yield (name, dataset)

    def get_name(self):
        return self.group.name

    def contains_dataset(self, dataset_name):
        return dataset_name in self.group

    def subgroup_exists(self, subgroup_name):
        return str(subgroup_name) in self.group

    def get_subgroup(self, child_group):
        group = self.group.get(str(child_group))
        if group is None:
            raise ValueError("Group: %s does not exist in: %s" % (child_group, group))
        if not isinstance(group, h5py.Group):
            raise TypeError("\"%s\" is not an hdf5 group!" % child_group)
        return Group(group)

    def create_subgroup(self, group_name):
        group_name = str(group_name)
        if group_name not in self.group:
            self.group.create_group(group_name)

    def get_all_subgroups(self):
        return (Group(group) for group in self.group.values() if isinstance(group, h5py.Group))

    def generate_dataset(self, dset_name, data):
        """
        Datasets with maxshape = ((None,)) so they can be extended
        max actual number of values we can store per array is 2^64 - 1
        data element needs to be converted to np.array first, otherwise it will
        be saved as a scalar, and won't be able to be extended later on into an array

        :param data: a list of data elements (string, int, float)
        """
        data = np.array(data, dtype=DSET_TYPES[dset_name])
        self.group.create_dataset(dset_name, data=data, maxshape=(None,), compression="gzip")

    def expand_dataset(self, dset_name, data):
        dset = self.group.get(dset_name)
        if dset is None:
            self.generate_dataset(dset_name, data)
        else:
            old_shape = dset.shape[0]
            data_length = len(data)
            dset.resize(((old_shape + data_length),))
            if data_length > 1:
                dset[old_shape:] = data
            else:
                dset[-1] = data

    def get_dset(self, dset_name, start, size):
        dset = self.group.get(dset_name)
        if dset is not None:
            if start <= dset.shape[0]:
                end = min(dset.shape[0], (start + size))
                return Dataset(dset[start:end])
        return Dataset([])

    def get_max_group_size(self):
        if self.contains_dataset(REFERENCE_DSET):
            return self.get_dset_shape(REFERENCE_DSET)[0]
        return 0

    def get_dset_shape(self, dset_name):
        if dset_name in self.group:
            return self.group[dset_name].shape
        else:
            raise ValueError("Dataset does not exist in group! dataset:", dset_name, " group:", self.group)

    def check_datasets_consistent(self, TO_STORE_DSETS):
        dsets = [self.group.get(dset_name) for dset_name in TO_STORE_DSETS]
        first_dset = dsets.pop()
        if first_dset is None:
            _assert_all_dsets_are_none(dsets)
        else:
            _assert_all_dsets_have_same_shape(first_dset, dsets)

    def is_value_in_dataset(self, element, dset_name):
        dataset = self.group.get(dset_name)
        if dataset is None:
            return False
        return element in dataset

    def load_datasets(self, dset_names, start, size):
        return {name : self.get_dset(name, start, size) for name in dset_names}

    def create_dataset_from_value(self, missing_value, start, size):
        reference_dset = self.get_dset(REFERENCE_DSET, start, size)
        create_size = min(len(reference_dset), size)
        return _create_dset_placeholder(missing_value, create_size)


def _assert_all_dsets_are_none(datasets):
    for dataset in datasets:
        assert dataset is None, "Group has datasets with inconsistent shape!"


def _assert_all_dsets_have_same_shape(first_dset, dsets):
    length = first_dset.shape[0]
    for dset in dsets:
        assert dset.shape[0] == length, \
            "Group has datasets with inconsistent shape!"


def _create_dset_placeholder(value, size):
    assert value is not None, "Can't create dataset with empty content!"
    return Dataset([value for _ in range(size)])