import numpy as np
from functools import reduce
import itertools
import sumstats.utils.pval_utils as pu


def get_group_from_parent(parent_group, child_group):
    group = parent_group.get(str(child_group))
    if group is None:
        raise ValueError("Group: %s does not exist in: %s" % (child_group, parent_group))
    return group


def get_all_groups_from_parent(parent_group):
    return [group for group in parent_group.values()]


def get_dset(group, dset_name):
    dset = group.get(dset_name)
    if dset is not None:
        dset = dset[:]
    return dset


def equality_mask(value, vector):
    _check_type_compatibility(value, vector)
    mask = None
    if value is not None:
        mask = [element == value for element in vector]

    return mask


def get_upper_limit_mask(upper_limit, vector):
    _check_type_compatibility(upper_limit, vector)
    mask = None
    if upper_limit is not None:
        mask = [element <= upper_limit for element in vector]
    return mask


def get_lower_limit_mask(lower_limit, vector):
    _check_type_compatibility(lower_limit, vector)
    mask = None
    if lower_limit is not None:
        mask = [element >= lower_limit for element in vector]
    return mask


def combine_list_of_masks(list_of_masks):
    not_none_masks = [mask for mask in list_of_masks if mask is not None]

    if len(not_none_masks) == 0:
        return None
    if len(not_none_masks) == 1:
        return not_none_masks[0]
    return reduce(lambda mask1, mask2: [all(tup) for tup in zip(mask1, mask2)], not_none_masks)


def interval_mask(lower_limit, upper_limit, vector):
    _check_type_compatibility(upper_limit, vector)
    _check_type_compatibility(lower_limit, vector)
    mask_u = get_upper_limit_mask(upper_limit, vector)
    mask_l = get_lower_limit_mask(lower_limit, vector)
    list_of_masks = [mask_l, mask_u]
    return combine_list_of_masks(list_of_masks)


def filter_by_mask(vector, mask):
    return list(itertools.compress(vector, mask))


def not_boolean_mask(mask):
    return not all(type(x) == bool or type(x) == np.bool_ for x in mask)


def filter_dictionary_by_mask(dictionary, mask):
    return {dset: filter_by_mask(dataset, mask) for dset, dataset in dictionary.items()}


def filter_dsets_with_restrictions(name_to_dataset, restrictions):
    print("r", restrictions)
    list_of_masks = [restriction.get_mask() for restriction in restrictions]

    filtering_mask = combine_list_of_masks(list_of_masks)
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



def _check_type_compatibility(value, vector):
    if value is None:
        return
    elif np.issubdtype(np.array([vector[0]]).dtype, int) and np.issubdtype(np.array([value]).dtype, int):
        return
    elif np.issubdtype(np.array([vector[0]]).dtype, float) and np.issubdtype(np.array([value]).dtype, float):
        return
    elif np.issubdtype(np.array([vector[0]]).dtype, str) and np.issubdtype(np.array([value]).dtype, str):
        return
    else:
        raise TypeError("Failed to create boolean mask of array of type "
                        "" + str(type(vector[0])) + ' using value of type ' + str(type(value)))
