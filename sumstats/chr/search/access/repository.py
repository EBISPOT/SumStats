
from sumstats.chr.constants import *
from sumstats.utils.dataset_utils import *


def load_datasets_from_groups(groups, start, size, study=None):
    return get_dsets_from_parent_group(groups, start, size, study)


def get_dsets_from_group(group, start, size):
    return group.load_datasets(dset_names=TO_QUERY_DSETS, start=start, size=size)

def create_empty_dataset():
    return create_dictionary_of_empty_dsets(TO_QUERY_DSETS)


def get_dsets_from_parent_group(group, start, size, study=None):
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
    datasets = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    end = start + size
    max_traversed = 0
    original_start = start

    for child_group in group:
        if study and study == child_group.get_name().split('/')[-1]:
            max_traversed += child_group.get_max_group_size()

            # we want to start higher than where we are now
            if original_start >= max_traversed:
                start = original_start - max_traversed
                continue

            total_retrieved = len(datasets[REFERENCE_DSET])
            if end <= total_retrieved:
                return datasets

            subset_of_datasets = get_dsets_from_group(child_group, start, size)
            datasets = extend_dsets_with_subset(datasets, subset_of_datasets)
            retrieved_size = len(subset_of_datasets[REFERENCE_DSET])

            max_traversed += retrieved_size
            size = size - retrieved_size
            # if I have already gathered some information
            # then I am going on to the next dataset and what to query it from its start
            start = _new_start_size(start=start, total_retrieved=len(datasets[REFERENCE_DSET]), retrieved=retrieved_size)

    return datasets


def _new_start_size(start, total_retrieved, retrieved):
    if total_retrieved > 0:
        return 0
    return start + retrieved


