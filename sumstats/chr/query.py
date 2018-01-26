"""
Utils useful for querying
"""

from sumstats.chr.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def load_datasets_from_groups(groups, start, size):
    return get_dsets_from_parent_group(groups, start, size)


def get_dsets_from_group(group, start, size):
    return group.load_datasets(dset_names=TO_QUERY_DSETS, start=start, size=size)


def get_dsets_from_parent_group(group, start, size):
    datasets = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

    end = start + size
    if isinstance(group, gu.Group):
        for child_group in group.get_values():
            dset_size = get_standard_group_dset_size(child_group)
            if group_has_groups(child_group):
                datasets = get_dsets_from_parent_group(child_group, start, size)
                dset_size = len(datasets[REFERENCE_DSET])

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
        # is a list
        print(group)
        for child_group in group:
            dset_size = get_standard_group_dset_size(child_group)
            if group_has_groups(child_group):
                datasets = get_dsets_from_parent_group(child_group, start, size)
                dset_size = len(datasets[REFERENCE_DSET])

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
    if group.contains_dataset(REFERENCE_DSET):
        return group.get_dset_shape(REFERENCE_DSET)[0]
    else:
        return 0


def group_has_groups(group):
    if isinstance(group, gu.Group):
        for name, item in group.get_items():
            #TODO figure this out! Need to hide hdf5 group
            return isinstance(item, gu.Group)
    else:
        return False


def continue_to_next_group(start, dset_size):
    return start >= dset_size


def calculate_remaining_size_from_data_subset(size, subset):
    retrieved_size = len(subset[REFERENCE_DSET])
    size = size - retrieved_size
    return size
