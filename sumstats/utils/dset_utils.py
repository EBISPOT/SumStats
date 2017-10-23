import numpy as np
from functools import reduce
import itertools


def equality_mask(value, dset):
    _check_type_compatibility(value, dset)
    mask = None
    if value is not None:
        mask = [element == value for element in dset]

    return mask


def get_upper_limit_mask(upper_limit, dset):
    _check_type_compatibility(upper_limit, dset)
    mask = None
    if upper_limit is not None:
        mask = [element <= upper_limit for element in dset]
    return mask


def get_lower_limit_mask(lower_limit, dset):
    _check_type_compatibility(lower_limit, dset)
    mask = None
    if lower_limit is not None:
        mask = [element >= lower_limit for element in dset]
    return mask


def combine_list_of_masks(list_of_masks):
    not_none_masks = [mask for mask in list_of_masks if mask is not None]

    if len(not_none_masks) == 0:
        return None
    if len(not_none_masks) == 1:
        return not_none_masks[0]
    return reduce(lambda mask1, mask2: [all(tup) for tup in zip(mask1, mask2)], not_none_masks)


def interval_mask(lower_limit, upper_limit, dset):
    _check_type_compatibility(upper_limit, dset)
    _check_type_compatibility(lower_limit, dset)
    mask_u = get_upper_limit_mask(upper_limit, dset)
    mask_l = get_lower_limit_mask(lower_limit, dset)
    list_of_masks = [mask_l, mask_u]
    return combine_list_of_masks(list_of_masks)


def filter_by_mask(dset, mask):
    return list(itertools.compress(dset, mask))


def _check_type_compatibility(value, dset):
    if value is None:
        return
    elif np.issubdtype(np.array([dset[0]]).dtype, int) and np.issubdtype(np.array([value]).dtype, int):
        return
    elif np.issubdtype(np.array([dset[0]]).dtype, float) and np.issubdtype(np.array([value]).dtype, float):
        return
    elif np.issubdtype(np.array([dset[0]]).dtype, str) and np.issubdtype(np.array([value]).dtype, str):
        return
    else:
        raise TypeError("Failed to create boolean mask of array of type "
                        "" + str(type(dset[0])) + ' using value of type ' + str(type(value)))