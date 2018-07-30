
from sumstats.snp.constants import *


def get_dsets_from_group(group, start, size):
    """
    Retrieves a slice of the SNP group's datasets
    :param group: the group we are traversing
    :param start: the offset we will start retrieving data from in the dataset (Dataset list)
    :param size: the number of data points that will be returned (size of the Dataset list)
    :return: a dictionary containing the dataset names and slices of the datasets
    """
    return group.load_datasets(dset_names=TO_QUERY_DSETS, start=start, size=size)