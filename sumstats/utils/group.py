"""
Utilities for hdf5 groups
"""

from sumstats.utils.dataset import Dataset
import numpy as np
from sumstats.common_constants import *


def subgroup_exists(parent_group, subgroup_name):
    return str(subgroup_name) in parent_group


def get_group_from_parent(parent_group, child_group):
    group = parent_group.get(str(child_group))
    if group is None:
        raise ValueError("Group: %s does not exist in: %s" % (child_group, parent_group))
    return group


def create_group_from_parent(parent_group, group_name):
    group_name = str(group_name)
    if group_name in parent_group:
        return parent_group.get(group_name)
    else:
        return parent_group.create_group(group_name)


def get_all_subgroups(parent_group):
    return [group for group in parent_group.values()]


def create_dataset(group, dset_name, data):
    """
    Datasets with maxshape = ((None,)) so they can be extended
    max actual number of values we can store per array is 2^64 - 1
    data element needs to be converted to np.array first, otherwise it will
    be saved as a scalar, and won't be able to be extended later on into an array

    :param data: a list of data elements (string, int, float)
    """
    data = np.array(data, dtype=DSET_TYPES[dset_name])
    group.create_dataset(dset_name, data=data, maxshape=(None,), compression="gzip")


def expand_dataset(group, dset_name, data):
    dset = group.get(dset_name)
    if dset is None:
        create_dataset(group, dset_name, data)
    else:
        last_index_before_resize = dset.shape[0]
        dset.resize(((dset.shape[0] + len(data)),))
        dset[last_index_before_resize:] = data


def get_dset(group, dset_name, start, size):
    dset = group.get(dset_name)
    if dset is not None:
        if start <= dset.shape[0]:
            end = min(dset.shape[0], (start + size))
            dset = dset[start:end]
    return dset


def check_group_dsets_shape(group, TO_STORE_DSETS):
    dsets = [group.get(dset_name) for dset_name in TO_STORE_DSETS]
    first_dset = dsets.pop()
    if first_dset is None:
        _assert_all_dsets_are_none(dsets)
    else:
        _assert_all_dsets_have_same_shape(first_dset, dsets)


def _assert_all_dsets_are_none(datasets):
    for dataset in datasets:
        assert dataset is None, "Group has datasets with inconsistent shape!"


def _assert_all_dsets_have_same_shape(first_dset, dsets):
    length = first_dset.shape[0]
    for dset in dsets:
        assert dset.shape[0] == length, \
            "Group has datasets with inconsistent shape!"


def value_in_dataset(group, element, dset_name):
    dataset = group.get(dset_name)
    if dataset is None:
        return False
    if element in dataset:
        return True
    return False


def load_dsets_from_group(group, dset_names, start, size):
    datasets = {}
    for name in dset_names:
        datasets[name] = _get_dset_from_group(name, group, start, size)

    return datasets


def create_dataset_from_value(missing_value, group, start, size):
    reference_dset = get_dset(group, REFERENCE_DSET, start, size)
    if reference_dset is None:
        # this group doesn't have any data so we won't create the dataset
        return []
    create_size = min(len(reference_dset), size)
    return _create_dset_placeholder(missing_value, create_size)


def _get_dset_from_group(dset_name, group, start, size):
    dataset = get_dset(group, dset_name, start, size)
    if dataset is None:
        dataset = []
    return Dataset(dataset)


def _create_dset_placeholder(value, size):
    assert value is not None, "Can't create dataset with empty content!"
    return Dataset([value for _ in range(size)])