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
    max_traversed = 0
    datasets = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    for child_group_name, child_group in group.get_items():
        group_max_size = get_group_dset_size(child_group)
        max_traversed += group_max_size

        if group_has_groups(child_group):
            subset_of_datasets = get_dsets_from_parent_group(child_group, start, size)
            datasets = extend_dsets_with_subset(datasets, subset_of_datasets)
            max_traversed += len(subset_of_datasets[REFERENCE_DSET])
        if continue_to_next_group(end, size, max_traversed):
            start = start - max_traversed
            continue

        subset_of_datasets = get_dsets_from_group_directly(child_group_name, child_group, start, size)
        datasets = extend_dsets_with_subset(datasets, subset_of_datasets)
        total_retrieved = len(datasets[REFERENCE_DSET])
        if end <= total_retrieved:
            return datasets

        retrieved_size = len(subset_of_datasets[REFERENCE_DSET])
        start = start - max_traversed + retrieved_size
        size = size - retrieved_size

    return datasets


def get_group_dset_size(group):
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


def continue_to_next_group(end, size, dset_size):
    return (end - size) >= dset_size


def get_dsets_from_group_directly(study, study_group, start, size):
    datasets =  study_group.load_datasets(TO_QUERY_DSETS, start, size)
    datasets[STUDY_DSET] = study_group.create_dataset_from_value(study, start, size)
    return datasets


def _assert_is_group(group):
    if not isinstance(group, gu.Group):
        raise KeyError("You didn't provide a group to search datasets from!")