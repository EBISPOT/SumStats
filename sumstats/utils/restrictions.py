"""
Classes that have a get_mask method
They impose restrictions to the datasets based on some criteria
"""

import sumstats.utils.pval as pu
from sumstats.utils.utils import logical_and_on_list_of_masks
from sumstats.utils.utils import logical_or_on_list_of_masks
import sumstats.utils.utils as utils
import sumstats.utils.interval as interval
from sumstats.common_constants import *


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
        exponent_on_limits = self._mask_for_values_on_exponent_limit()
        exponent_between_limits = self._mask_for_values_between_exponent_limits()
        return logical_or_on_list_of_masks([exponent_on_limits, exponent_between_limits])

    def _mask_for_values_on_exponent_limit(self):
        lower_exponent = self.exponent.equality_mask(self.exp_lower)
        upper_exponent = self.exponent.equality_mask(self.exp_upper)

        mantissa_lower_limit = self.mantissa.get_lower_limit_mask(self.mantissa_lower)
        mantissa_upper_limit = self.mantissa.get_upper_limit_mask(self.mantissa_upper)

        lower_limit = logical_and_on_list_of_masks(
            [lower_exponent, mantissa_lower_limit])
        upper_limit = logical_and_on_list_of_masks(
            [upper_exponent, mantissa_upper_limit])

        return self._combine_limit_masks(lower_limit, upper_limit)

    def _combine_limit_masks(self, lower_limit_mask, upper_limit_mask):
        if self.exp_lower == self.exp_upper:
            # if we have the same exponent, we need to cutoff the mantissas
            mask_for_exponent_equality = logical_and_on_list_of_masks([lower_limit_mask, upper_limit_mask])
        else:
            # if exponent is different, it makes no sense to compare the mantissas
            mask_for_exponent_equality = logical_or_on_list_of_masks([lower_limit_mask, upper_limit_mask])
        return mask_for_exponent_equality

    def _mask_for_values_between_exponent_limits(self):
        mask_between_exp_limits = None

        new_exp_lower = self.exp_lower + 1
        new_exp_upper = self.exp_upper - 1
        if new_exp_lower <= new_exp_upper:
            mask_between_exp_limits = self.exponent.interval_mask(new_exp_lower, new_exp_upper)

        return mask_between_exp_limits


def apply_restrictions(name_to_dataset, snp=None, study=None, chr=None, pval_interval=None, bp_interval=None):
    restrictions = []
    if dataset_present(SNP_DSET, name_to_dataset) and snp is not None:
        restriction = snp
        dataset = name_to_dataset[SNP_DSET]
        restrictions.append(get_restriction(restriction, dataset))
    if dataset_present(STUDY_DSET, name_to_dataset) and study is not None:
        restriction = study
        dataset = name_to_dataset[STUDY_DSET]
        restrictions.append(get_restriction(restriction, dataset))
    if dataset_present(CHR_DSET, name_to_dataset) and chr is not None:
        restriction = chr
        dataset = name_to_dataset[CHR_DSET]
        restrictions.append(get_restriction(restriction, dataset))
    if dataset_present(MANTISSA_DSET, name_to_dataset) and pval_interval is not None:
        restriction = pval_interval
        dataset_mantissa = name_to_dataset[MANTISSA_DSET]
        dataset_exp = name_to_dataset[EXP_DSET]
        restrictions.append(get_restriction(restriction, (dataset_mantissa, dataset_exp)))
    if dataset_present(BP_DSET, name_to_dataset) and bp_interval is not None:
        restriction = bp_interval
        dataset = name_to_dataset[BP_DSET]
        restrictions.append(get_restriction(restriction, dataset))

    if restrictions:
        return filter_dsets_with_restrictions(name_to_dataset, restrictions)

    return name_to_dataset


def dataset_present(dataset_name, dictionary):
    return dataset_name in dictionary


def get_restriction(restriction, datasets):
    if interval.is_interval(restriction):
        if datasets.__class__ == tuple:
            return IntervalRestrictionPval(restriction.floor(), restriction.ceil(), datasets[0], datasets[1])
        else:
            return IntervalRestriction(restriction.floor(), restriction.ceil(), datasets)
    else:
        return EqualityRestriction(restriction, datasets)


def filter_dsets_with_restrictions(name_to_dataset, restrictions):
    list_of_masks = [restriction.get_mask() for restriction in restrictions]

    filtering_mask = logical_and_on_list_of_masks(list_of_masks)
    if filtering_mask is not None:
        return utils.filter_dictionary_by_mask(name_to_dataset, filtering_mask)

    return name_to_dataset


