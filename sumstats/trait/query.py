from sumstats.trait.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def get_dsets_from_file(f, start, size):
    return get_dsets_from_parent_group(f, start, size)


def get_dsets_from_trait_group(trait_group, start, size):
    return get_dsets_from_parent_group(trait_group, start, size)


def get_dsets_from_parent_group(group, start, size):
    end = start + size
    print("start, size, end", start, size, end)
    all_groups_size = 0

    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

    for child_group_name, child_group in group.items():
        dset_size = get_standard_group_dset_size(child_group)
        all_groups_size += dset_size
        if group_has_groups(child_group):
            subset_of_datasets = get_dsets_from_parent_group(child_group, start, size)
            name_to_dataset = extend_dsets_with_subset(name_to_dataset, subset_of_datasets)
            dset_size = len(name_to_dataset[REFERENCE_DSET])
            all_groups_size += dset_size
        if continue_to_next_group(start, all_groups_size):
            start, size = calculate_remaining_start_and_size(0, all_groups_size, start, size)
            continue
        else:
            subset_of_datasets = get_dsets_from_group_directly(child_group_name, child_group, start, size)
            name_to_dataset = extend_dsets_with_subset(name_to_dataset, subset_of_datasets)
            if end <= dset_size:
                return name_to_dataset
            else:
                retrieved_size = len(subset_of_datasets[REFERENCE_DSET])
                start, size = calculate_remaining_start_and_size(retrieved_size, all_groups_size, start, size)
                continue
    print(name_to_dataset[STUDY_DSET])
    return name_to_dataset


def get_standard_group_dset_size(group):
    if REFERENCE_DSET in group:
        return group.get(REFERENCE_DSET).shape[0]
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


def extend_dsets_with_subset(name_to_dataset, subset):
    for dset_name, dataset in name_to_dataset.items():
        dataset.extend(subset[dset_name])
    return name_to_dataset


def calculate_remaining_start_and_size(retrieved_size, groups_size, start, size):
    size = size - retrieved_size
    start = start - groups_size + retrieved_size
    return start, size


def get_dsets_from_group_directly(study, study_group, start, size):
    name_to_dataset = gu.load_dsets_from_group(study_group, TO_QUERY_DSETS, start, size)
    name_to_dataset[STUDY_DSET] = gu.create_dataset_from_value(study, size)
    return name_to_dataset