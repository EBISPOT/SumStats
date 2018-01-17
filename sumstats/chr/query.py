"""
Utils useful for querying
"""

from sumstats.chr.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def load_datasets_from_groups(groups, start, size):
    return get_dsets_from_parent_group(groups, start, size)


def get_dsets_from_group(group, start, size):
    return gu.load_dsets_from_group(group=group, dset_names=TO_QUERY_DSETS, start=start, size=size)


def get_dsets_from_parent_group(group, start, size):
    datasets = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

    end = start + size
    if isinstance(group, h5py._hl.group.Group):
        for child_group_name, child_group in group.items():
            dset_size = get_standard_group_dset_size(child_group)
            if group_has_groups(child_group):
                datasets = get_dsets_from_parent_group(child_group, start, size)
                dset_size = len(datasets[MANTISSA_DSET])

            if continue_to_next_group(start, dset_size):
                continue
            else:
                subset_of_datasets = get_dsets_from_group(child_group, start, size)
                datasets = extend_dsets_with_subset(datasets, subset_of_datasets)

                if end <= dset_size:
                    return datasets
                else:
                    size = calculate_remaining_size_from_data_subset(size, subset_of_datasets)
                    continue
        return datasets
    else:
        for child_group in group:
            dset_size = get_standard_group_dset_size(child_group)
            if group_has_groups(child_group):
                datasets = get_dsets_from_parent_group(child_group, start, size)
                dset_size = len(datasets[MANTISSA_DSET])

            if continue_to_next_group(start, dset_size):
                print("next group")
                continue
            else:
                subset_of_datasets = get_dsets_from_group(child_group, start, size)
                datasets = extend_dsets_with_subset(datasets, subset_of_datasets)

                if end <= dset_size:
                    return datasets
                else:
                    size = calculate_remaining_size_from_data_subset(size, subset_of_datasets)
                    continue
        return datasets


def get_standard_group_dset_size(group):
    if MANTISSA_DSET in group:
        return group.get(MANTISSA_DSET).shape[0]
    else:
        return 0


def group_has_groups(group):
    if isinstance(group, h5py._hl.group.Group):
        for name, item in group.items():
            return isinstance(item, h5py._hl.group.Group)
    else:
        return False


def continue_to_next_group(start, dset_size):
    return start >= dset_size


def calculate_remaining_size_from_data_subset(size, subset):
    retrieved_size = len(subset[MANTISSA_DSET])
    size = size - retrieved_size
    return size
