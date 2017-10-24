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


def get_dset(group, dset_name):
    dset = group.get(dset_name)
    if dset is not None:
        dset = dset[:]
    return dset


def extend_dsets_for_group(group_name, group, name_to_dataset, missing_dset, existing_dset):
    for name, dataset in name_to_dataset.items():
        if name != missing_dset:
            dataset.extend(_get_dset_from_group(name, group))

    temp_dset = _get_dset_from_group(existing_dset, group)
    name_to_dataset[missing_dset].extend(_create_dset_placeholder(len(temp_dset), group_name))
    return name_to_dataset


def _get_dset_from_group(dset_name, group):
    dataset = get_dset(group, dset_name)
    if dataset is None:
        raise LookupError("Dataset empty: ", dset_name)
    return Dataset(dataset)


def _create_dset_placeholder(size, value):
    assert value is not None, "Can't create dataset with empty content!"
    return Dataset([value for _ in range(size)])