from sumstats.trait.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def get_dsets_from_file_group(file_group, start, size):
    _assert_is_group(file_group)
    return get_dsets_from_parent_group(file_group, start, size)


def get_dsets_from_trait_group(trait_group, start, size):
    _assert_is_group(trait_group)
    return get_dsets_from_parent_group(trait_group, start, size)


def get_dsets_from_parent_group(group, start, size):
    _assert_is_group(group)
    end = start + size
    all_groups_size = 0

    datasets = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    for child_group_name, child_group in group.get_items():
        dset_size = get_standard_group_dset_size(child_group)
        all_groups_size += dset_size
        if group_has_groups(child_group):
            subset_of_datasets = get_dsets_from_parent_group(child_group, start, size)
            datasets = extend_dsets_with_subset(datasets, subset_of_datasets)
            dset_size = len(datasets[REFERENCE_DSET])
            all_groups_size += dset_size
        if continue_to_next_group(start, all_groups_size):
            start, size = calculate_remaining_start_and_size(0, all_groups_size, start, size)
            continue
        else:
            subset_of_datasets = get_dsets_from_group_directly(child_group_name, child_group, start, size)
            datasets = extend_dsets_with_subset(datasets, subset_of_datasets)
            if end <= dset_size:
                return datasets
            else:
                retrieved_size = len(subset_of_datasets[REFERENCE_DSET])
                start, size = calculate_remaining_start_and_size(retrieved_size, all_groups_size, start, size)
                continue

    return datasets


def get_standard_group_dset_size(group):
    if group.contains_dataset(REFERENCE_DSET):
        return group.get_dset_shape(REFERENCE_DSET)[0]
    else:
        return 0


def group_has_groups(group):
    if isinstance(group, gu.Group):
        for value in group.get_values():
            return isinstance(value, gu.Group)
    else:
        return False


def continue_to_next_group(start, dset_size):
    return start >= dset_size


def calculate_remaining_start_and_size(retrieved_size, groups_size, start, size):
    size = size - retrieved_size
    start = start - groups_size + retrieved_size
    return start, size


def get_dsets_from_group_directly(study, study_group, start, size):
    datasets =  study_group.load_datasets(TO_QUERY_DSETS, start, size)
    datasets[STUDY_DSET] = study_group.create_dataset_from_value(study, start, size)
    return datasets


def _assert_is_group(group):
    if not isinstance(group, gu.Group):
        raise KeyError("You didn't provide a group to search datasets from!")