"""
Utilities for hdf5 groups
"""

from sumstats.utils.dataset import Dataset


def get_group_from_parent(parent_group, child_group):
    group = parent_group.get(str(child_group))
    if group is None:
        raise ValueError("Group: %s does not exist in: %s" % (child_group, parent_group))
    return group


def get_all_groups_from_parent(parent_group):
    return [group for group in parent_group.values()]


def get_dset(group, dset_name, start, size):
    dset = group.get(dset_name)
    if dset is not None:
        if start <= dset.shape[0]:
            end = min(dset.shape[0], (start + size))
            dset = dset[start:end]
        else:
            dset = None
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


def check_element_not_loaded_in_dset(group, element, dset_name):
    dataset = group.get(dset_name)
    if dataset is None:
        return
    if element in dataset:
        raise AssertionError(element + " already exists in " + dset_name + "!")


def extend_dsets_for_group(group, name_to_dataset, start, size):
    for name, dataset in name_to_dataset.items():
        dataset.extend(_get_dset_from_group(name, group, start, size))

    return name_to_dataset


def extend_dsets_for_group_missing(missing_value, group, name_to_dataset, missing_dset, start, size):
    size_of_new_dataset = 0
    for name, dataset in name_to_dataset.items():
        if name != missing_dset:
            dset = _get_dset_from_group(name, group, start, size)
            size_of_new_dataset = len(dset)
            dataset.extend(dset)
    name_to_dataset[missing_dset].extend(_create_dset_placeholder(size_of_new_dataset, missing_value))
    return name_to_dataset


def _get_dset_from_group(dset_name, group, start, size):
    dataset = get_dset(group, dset_name, start, size)
    if dataset is None:
        dataset = []
    return Dataset(dataset)


def _create_dset_placeholder(size, value):
    assert value is not None, "Can't create dataset with empty content!"
    return Dataset([value for _ in range(size)])