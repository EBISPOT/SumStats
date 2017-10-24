"""
General methods used across the modules
"""

import sumstats.utils.pval as pu
from sumstats.utils.dataset import *


def filter_dictionary_by_mask(dictionary, mask):
    return {dset: Dataset(dataset.filter_by_mask(mask)) for dset, dataset in dictionary.items()}


def filter_dsets_with_restrictions(name_to_dataset, restrictions):
    list_of_masks = [restriction.get_mask() for restriction in restrictions]

    filtering_mask = combine_list_of_masks(list_of_masks)
    if filtering_mask is not None:
        return filter_dictionary_by_mask(name_to_dataset, filtering_mask)

    return name_to_dataset


def assert_datasets_not_empty(name_to_dataset):
    for dset_name, dataset in name_to_dataset.items():
        if empty_array(dataset):
            raise ValueError("Array is None or empty: " + dset_name)


def empty_array(array):
    if array is None:
        return True
    if len(array) == 0:
        return True
    return False


def get_mantissa_and_exp_lists(string_list):
    mantissa_dset = []
    exp_dset = []
    for str_number in string_list:
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        mantissa_dset.append(mantissa)
        exp_dset.append(exp)

    return mantissa_dset, exp_dset


def create_datasets_from_lists(name_to_dsets):
    return {dset_name : Dataset(dset_vector) for dset_name, dset_vector in name_to_dsets.items()}


def create_dictionary_of_empty_dsets(names):
    return {name : Dataset([]) for name in names}

