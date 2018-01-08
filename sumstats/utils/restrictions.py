"""
Classes that have a get_mask method
They impose restrictions to the datasets based on some criteria
"""

import sumstats.utils.pval as pu
from sumstats.utils.utils import logical_and_on_list_of_masks
from sumstats.utils.utils import logical_or_on_list_of_masks


class IntervalRestriction():
    def __init__(self, lower, upper, dataset):
        assert lower <= upper, "Lower limit must be numerically lower than upper limit!"
        self.lower = lower
        self.upper = upper
        self.dataset = dataset

    def get_mask(self):
        return self.dataset.interval_mask(self.lower, self.upper)


class EqualityRestriction():
    def __init__(self, value, dataset):
        self.value = value
        self.dataset = dataset

    def get_mask(self):
        return self.dataset.equality_mask(self.value)


class IntervalRestrictionPval():
    def __init__(self, lower, upper, mantissa_dset, exponent_dset):
        assert lower <= upper, "Lower limit must be numerically lower than upper limit!"
        self.mantissa_lower, self.exp_lower = pu.convert_to_mantissa_and_exponent(str(lower))
        self.mantissa_upper, self.exp_upper = pu.convert_to_mantissa_and_exponent(str(upper))
        self.mantissa = mantissa_dset
        self.exponent = exponent_dset

    def get_mask(self):
        same_lower_exp_mask = self.exponent.equality_mask(self.exp_lower)
        same_upper_exp_mask = self.exponent.equality_mask(self.exp_upper)
        mantissa_mask = self.mantissa.interval_mask(self.mantissa_lower, self.mantissa_upper)

        mask_lower = logical_and_on_list_of_masks([same_lower_exp_mask, mantissa_mask])
        mask_upper = logical_and_on_list_of_masks([same_upper_exp_mask, mantissa_mask])

        mask_exp_interval = None
        new_lower = self.exp_lower + 1
        new_upper = self.exp_upper - 1
        if new_lower <= new_upper:
            mask_exp_interval = self.exponent.interval_mask(new_lower, new_upper)

        return logical_or_on_list_of_masks([mask_lower, mask_upper, mask_exp_interval])
