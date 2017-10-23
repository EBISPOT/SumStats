import numpy as np
import sumstats.utils.pval_utils as pu
import sumstats.utils.dset_utils as du


def filter_dictionary_by_mask(dictionary, mask):
    return {dset: du.filter_by_mask(dataset, mask) for dset, dataset in dictionary.items()}


def filter_dsets_with_restrictions(name_to_dataset, restrictions):
    list_of_masks = [restriction.get_mask() for restriction in restrictions]

    filtering_mask = du.combine_list_of_masks(list_of_masks)
    if filtering_mask is not None:
        return filter_dictionary_by_mask(name_to_dataset, filtering_mask)

    return name_to_dataset


def convert_lists_to_np_arrays(dictionary, dset_types):
    return {dset_name: np.array(dataset, dtype=dset_types[dset_name]) for dset_name, dataset in dictionary.items()}


def remove_headers(name_to_dataset, column_headers):
    for column in column_headers:
        if column == name_to_dataset[column][0]:
            name_to_dataset[column] = name_to_dataset[column][1:]
        else:
            raise ValueError("Headers in file to not match defined column names: " + str(column_headers))
    return name_to_dataset


def assert_np_datasets_not_empty(name_to_dataset):
    for dset_name, dataset in name_to_dataset.items():
        if empty_np_array(dataset):
            raise ValueError("Array is None or empty: " + dset_name)


def empty_np_array(array):
    if array.tolist() is None:
        return True
    if len(array) == 0:
        return True
    return False


def get_mantissa_and_exp_dsets(string_list):
    mantissa_dset = []
    exp_dset = []
    for str_number in string_list:
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        mantissa_dset.append(mantissa)
        exp_dset.append(exp)

    return mantissa_dset, exp_dset

