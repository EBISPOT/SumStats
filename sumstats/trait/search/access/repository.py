
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
    """
    Traverses the subgroups of the given group and retrieves the data stored in their datasets.
    It traverses the datasets of the first subgroup before it continues to the next subgroup's datasets.
    It uses start and size to see if it needs to skip a subgroup all together (i.e. start is bigger than the size of the
    subgroups datasets).
    :param group: the group who's data we want to retrieve
    :param start: the offset we will start retrieving data from in the dataset (Dataset list)
    :param size: the number of data points that will be returned (size of the Dataset list)
    :return: a dictionary containing the dataset names and slices of the datasets
    """
    _assert_is_group(group)
    original_start = start
    end = start + size
    max_traversed = 0
    datasets = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    for child_group_name, child_group in group.get_items():
        max_traversed += child_group.get_max_group_size()

        datasets, size_of_children = _gather_all_children(child_group=child_group, datasets=datasets, start=start, size=size)
        max_traversed += size_of_children
        # we want to start higher than where we are now
        if original_start >= max_traversed:
            start = original_start - max_traversed
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


def _assert_is_group(group):
    if not isinstance(group, gu.Group):
        raise KeyError("You didn't provide a group to search datasets from!")


def _gather_all_children(child_group, datasets, start, size):
    if _group_has_groups(child_group):
        subset_of_datasets = get_dsets_from_parent_group(child_group, start, size)
        datasets = extend_dsets_with_subset(datasets, subset_of_datasets)
        return datasets, len(subset_of_datasets[REFERENCE_DSET])
    return datasets, 0


def _group_has_groups(group):
    if isinstance(group, gu.Group):
        for value in group.get_values():
            return isinstance(value, gu.Group)
    return False


def get_dsets_from_group_directly(study, study_group, start, size):
    """
    Retrives the datasets from a study group
    :param study: the study accession (a dataset populated by this value will be created)
    :param study_group: the study group we are querying
    :param start: the offset we will start retrieving data from in the dataset (Dataset list)
    :param size: the number of data points that will be returned (size of the Dataset list)
    :return: a dictionary containing the dataset names and slices of the datasets
    """
    datasets =  study_group.load_datasets(TO_QUERY_DSETS, start, size)
    datasets[STUDY_DSET] = study_group.create_dataset_from_value(study, start, size)
    return datasets