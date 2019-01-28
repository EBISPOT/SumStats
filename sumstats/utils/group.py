"""
Utilities for hdf5 groups
"""

from sumstats.utils.dataset import Dataset
import numpy as np
from sumstats.common_constants import *
from sumstats.errors.error_classes import *
import itertools


class Group:
    def __init__(self, group):
        # an actual HDF5 group
        if not (isinstance(group, h5py.Group) or isinstance(group, h5py.File)):
            raise TypeError("Trying to intialize Group object with something other than a hdf5 group or hdf5 file!")
        self.group = group

    def get_values(self):
        """
        Get all the values of a group: can be other groups and so they need to be
        wrapped in a Group object, or they can be Datasets.
        :return: a generator that you can iterate through to get the values of the group
        """
        for dataset in self.group.values():
            if isinstance(dataset, h5py.Group):
                yield Group(dataset)
            else:
                yield dataset

    def get_items(self):
        """
        Get all items of a group, i.e. (name, object) pairs. The items can be other
        groups and so they need to be wrapped in a Group object, or they can be Datasets.
        :return: a generator that you can iterate through to get the items of the group
        """
        for name, dataset in self.group.items():
            if isinstance(dataset, h5py.Group):
                yield (name, Group(dataset))
            else:
                yield (name, dataset)

    def get_name(self):
        return self.group.name

    def get_parent(self):
        return Group(self.group.parent)

    def contains_dataset(self, dataset_name):
        """
        :param dataset_name: a dataset we are looking for in the group
        :return: True or False if the dataset is stored in the group
        """
        return dataset_name in self.group

    def subgroup_exists(self, subgroup_name):
        """
        :param subgroup_name: a group name we are looking for in the group
        :return: True of False if it is a subgroup of our group (self)
        """
        return str(subgroup_name) in self.group

    def get_subgroup(self, child_group):
        group = self.group.get(str(child_group))
        if group is None:
            self._raise_non_existent_subgroup_error(child_group)
        if not isinstance(group, h5py.Group):
            raise TypeError("\"%s\" is not an hdf5 group!" % child_group)
        return Group(group)

    def create_subgroup(self, group_name):
        group_name = str(group_name)
        if group_name not in self.group:
            self.group.create_group(group_name)

    def get_all_subgroups(self):
        """
        Get's all the subgroups of our group (self)
        :return: a generator that you can iterate through to get all the subgroups of our group
        """
        return (Group(group) for group in self.group.values() if isinstance(group, h5py.Group))

    def get_all_subgroups_keys(self):
        return sorted(list(self.group.keys()))

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
        """
        Expands a groups' dataset with new data (data point or list of data points)
        :param dset_name: the name of the dataset being expanded
        :param data: the data added: single data point or list of data
        """
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
        """
        :param dset_name: the name of the dataset we are interested in
        :param start: the offset we will start retrieving data from in the dataset (Dataset list)
        :param size: the number of data points that will be returned (size of the Dataset list)
        :return: Subset of the Dataset list based on start and size,
        or empty Dataset if it doesn't exist or out of bounds
        """
        dset = self.group.get(dset_name)
        if dset is not None:
            if start <= dset.shape[0]:
                end = min(dset.shape[0], (start + size))
                return Dataset(dset[start:end])
        return Dataset([])

    def get_max_group_size(self):
        """
        :return: the size of the Datasets that are stored under the group
        """
        #print('getting size')
        if self.contains_dataset(REFERENCE_DSET):
            #return self.get_dset_shape(REFERENCE_DSET)[0]
            return self.get_dset_len(REFERENCE_DSET)
        return 0


    def get_dset_len(self, dset_name):
        if dset_name in self.group:
            return self.group[dset_name].len()
        else:
            self._raise_non_existent_subgroup_error(dset_name)

    def get_dset_shape(self, dset_name):
        if dset_name in self.group:
            return self.group[dset_name].shape
        else:
            self._raise_non_existent_subgroup_error(dset_name)

    def check_datasets_consistent(self, TO_STORE_DSETS):
        """
        Checks to see if the datasets under the group are all of the same shape
        :param TO_STORE_DSETS: a set of all the names of the stored datasets
        :return: True or False based on the consistency of the datasets
        """
        dsets = [self.group.get(dset_name) for dset_name in TO_STORE_DSETS]
        _assert_all_dsets_have_same_shape(dsets)

    def is_value_in_dataset(self, element, dset_name):
        dataset = self.group.get(dset_name)
        if dataset is None:
            return False
        return element in dataset

    def load_datasets(self, dset_names, start, size):
        """
        Load datasets into memory
        :param dset_names: the names of the datasets that we are loading into memory (in a dictionary)
        :param start: the offset we will start retrieving data from in the dataset (Dataset list)
        :param size: the number of data points that will be returned (size of the Dataset list)
        :return: the dictionary containing the names of the datasets requested and
        a subset of the Dataset lists based on start and size
        """
        return {name : self.get_dset(name, start, size) for name in dset_names}

    def create_dataset_from_value(self, missing_value, start, size):
        """
        Create a dataset of a specific size where missing_value will populate all the elements of the dataset
        :param missing_value: the value to populate the dataset with
        :param start: the offset we will start retrieving data from the reference dataset
        :param size: the number of data points that will be returned (size of the Dataset list)
        :return: a dataset where all elements are populated with 'missing_value'
        """
        reference_dset = self.get_dset(REFERENCE_DSET, start, size)
        create_size = min(len(reference_dset), size)
        return _create_dset_placeholder(missing_value, create_size)

    def set_attribute(self, key, value):
        self.group.attrs[key] = value

    def get_attribute(self, key):
        return self.group.attrs[key]

    def get_attribute(self, key):
        if key in self.group.attrs:
            return self.group.attrs[key]
        else:
            return None


    def get_dict_of_attributes(self):
        return self.group.attrs.items()


    def _raise_non_existent_subgroup_error(self, child_group):
        if self.group.name == "/":
            raise NotFoundError(item_not_found=child_group)
        else:
            parent_name = self.group.name.split("/")[-1]
        raise SubgroupError(parent="parent group: " + parent_name,
                            subgroup="sub group: " + str(child_group))


def generate_subgroups_from_generator_of_subgroups(generator):
    """
    The Group method get_all_subgroups() returns a generator of subgroups.
    If we need the subgroups of each of those subgroups, we need to return a generator of generators!
    E.g. We have a generator of bp blocks (subgroups) for a given chr (group), but we want the subgroups of
    those bp blocks (which are the studies, so we use this function to achieve this.
    For this, we use the itertools.chain method.
    :param generator: the generator from the get_all_subgroups()
    :return: a generator of subgroups of the generator of subgroups
    """
    return itertools.chain.from_iterable(
        subgroup.get_all_subgroups()
        for subgroup in generator
    )


def _assert_all_dsets_have_same_shape(dsets):
    first_dset = _get_first_non_empty_dset(dsets)
    if first_dset is not None:
        length = first_dset.shape[0]
        for dset in dsets:
            if dset is not None:
                assert dset.shape[0] == length, \
                    "Group has datasets with inconsistent shape!"


def _get_first_non_empty_dset(dsets):
    while len(dsets) > 0:
        # get the first dataset that is not None
        first_dset = dsets.pop()
        if first_dset is not None:
            return first_dset
    return None


def _create_dset_placeholder(value, size):
    assert value is not None, "Can't create dataset with empty content!"
    return Dataset([value for _ in range(size)])