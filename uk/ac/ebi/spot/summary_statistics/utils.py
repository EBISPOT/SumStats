import numpy as np


def get_group_from_parent(parent_group, child_group):
    group = parent_group.get(str(child_group))
    if group is None:
        raise ValueError("Group: %s does not exist in: %s" % (child_group, parent_group))
    return group


def get_dset(group, dset_name):
    dset = group.get(dset_name)
    if dset is not None:
        dset = dset[:]
    return dset


def get_upper_limit_mask(upper_limit, vector):
    _check_type_compatibility(upper_limit, vector)
    mask = None
    if upper_limit is not None:
        mask = vector <= upper_limit
    return mask


def get_lower_limit_mask(lower_limit, vector):
    _check_type_compatibility(lower_limit, vector)
    mask = None
    if lower_limit is not None:
        mask = vector >= lower_limit
    return mask


def combine_masks(mask1, mask2):
    if mask1 is None:
        return mask2
    if mask2 is None:
        return mask1
    return [all(tup) for tup in zip(mask1, mask2)]


def cutoff_mask(vector, upper_limit, lower_limit):
    _check_type_compatibility(upper_limit, vector)
    _check_type_compatibility(lower_limit, vector)
    mask_u = get_upper_limit_mask(upper_limit, vector)
    mask_l = get_lower_limit_mask(lower_limit, vector)
    return combine_masks(mask_u, mask_l)


def get_equality_mask(value, vector):
    _check_type_compatibility(value, vector)
    mask = None
    if value is not None:
        mask = vector == value

    return mask


# This needs to be tested for performance issues
def filter_by_mask(vector, mask):
    if not all(type(x) == bool or type(x) == np.bool_ for x in mask):
        raise TypeError("Trying to filter vector using non boolean mask")
    return vector[mask]


def filter_dictionary_by_mask(dictionary, mask):
    for dset in dictionary:
        dictionary[dset] = filter_by_mask(dictionary[dset], mask)

    return dictionary


def _check_type_compatibility(value, vector):
    both_strings = False
    if np.issubdtype(vector.dtype, str) and np.issubdtype(np.array([value]).dtype, str):
        both_strings = True

    if np.array([value]).dtype != vector.dtype and not both_strings:
        raise TypeError("Failed to create boolean mask of array of type "
                        "" + str(vector.dtype) + ' using value of type ' + str(np.array([value]).dtype))