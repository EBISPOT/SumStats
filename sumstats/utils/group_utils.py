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


def get_dset_from_group(dset_name, group):
    dataset = get_dset(group, dset_name)
    if dataset is None:
        raise LookupError("Dataset empty: ", dset_name)
    return Dataset(dataset)


def create_dset_placeholder(size, value):
    assert value is not None, "Can't create dataset with empty content!"
    return Dataset([value for _ in range(size)])