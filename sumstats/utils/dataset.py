"""
Dataset class is a wrapper for a plain list
Each hdf5 dataset here is represented as a list (or vector)
We have wrapped the simple list with a set of methods that
can filter the list
"""

import numpy as np
import itertools
from functools import reduce


class Dataset(list):

    def equality_mask(self, value):
        self._check_type_compatibility(value)
        mask = None
        if value is not None:
            mask = [element == value for element in self]

        return mask

    def get_upper_limit_mask(self, upper_limit):
        self._check_type_compatibility(upper_limit)
        mask = None
        if upper_limit is not None:
            mask = [element <= upper_limit for element in self]
        return mask

    def get_lower_limit_mask(self, lower_limit):
        self._check_type_compatibility(lower_limit)
        mask = None
        if lower_limit is not None:
            mask = [element >= lower_limit for element in self]
        return mask

    def interval_mask(self, lower_limit, upper_limit):
        self._check_type_compatibility(upper_limit)
        self._check_type_compatibility(lower_limit)
        if lower_limit is not None and upper_limit is not None:
            assert lower_limit <= upper_limit, "Lower limit must be numerically lower than upper limit!"
        mask_u = self.get_upper_limit_mask(upper_limit)
        mask_l = self.get_lower_limit_mask(lower_limit)
        list_of_masks = [mask_l, mask_u]
        return logical_and_on_list_of_masks(list_of_masks)

    def filter_by_mask(self, mask):
        return list(itertools.compress(self, mask))

    def _check_type_compatibility(self, value):
        if value is None:
            return
        elif np.int64 == np.array([self[0]]).dtype and  np.int64 == np.array([value]).dtype:
            return
        elif np.float64 == np.array([self[0]]).dtype and np.float64 == np.array([value]).dtype:
            return
        elif np.str_ == np.dtype(np.array([self[0]]).dtype).type and np.str_ == np.dtype(np.array([value]).dtype).type:
            return
        else:
            raise TypeError("Failed to create boolean mask of array of type "
                            "" + str(type(self[0])) + ' using value of type ' + str(type(value)))


def logical_and_on_list_of_masks(list_of_masks):
    not_none_masks = [mask for mask in list_of_masks if mask is not None]

    if len(not_none_masks) == 0:
        return None
    if len(not_none_masks) == 1:
        return not_none_masks[0]
    return reduce(lambda mask1, mask2: [all(tup) for tup in zip(mask1, mask2)], not_none_masks)


def logical_or_on_list_of_masks(list_of_masks):
    not_none_masks = [mask for mask in list_of_masks if mask is not None]

    if len(not_none_masks) == 0:
        return None
    if len(not_none_masks) == 1:
        return not_none_masks[0]
    return reduce(lambda mask1, mask2: [any(tup) for tup in zip(mask1, mask2)], not_none_masks)