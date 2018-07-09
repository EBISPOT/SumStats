"""
Classes that have a get_mask method/ and complementary methods to apply restrictions to datasets
They impose restrictions to the datasets based on some criteria

A restriction is created based on a restriction which is a value or value interval and the dataset that restriction
is referring to. Once the restriction mask is created based on these criteria, it is applied to all of datasets.

Example: if I want to query my datasets based on the study accession, I will first create the mask based on the
study accession value I want and the the study_accession dataset, and then apply that mask on ALL of the datasets.
"""

import sumstats.utils.pval as pu
from sumstats.utils.utils import logical_and_on_list_of_masks
from sumstats.utils.utils import logical_or_on_list_of_masks
import sumstats.utils.utils as utils
import sumstats.utils.interval as interval
from sumstats.common_constants import *


class IntervalRestriction:
    """
    Applies a lower AND upper limit mask to the dataset (inclusive) and discards any data point that is outside of this
    interval.
    """
    def __init__(self, lower, upper, dataset):
        if lower is not None and upper is not None:
            if lower > upper:
                raise ValueError("Lower limit must be numerically lower than upper limit!")
        self.lower = lower
        self.upper = upper
        self.dataset = dataset

    def get_mask(self):
        return self.dataset.interval_mask(self.lower, self.upper)


class EqualityRestriction:
    """
    Restricts the data that are equal to the value provieded, and discards all the other data points.
    """
    def __init__(self, value, dataset):
        self.value = value
        self.dataset = dataset

    def get_mask(self):
        return self.dataset.equality_mask(self.value)


class IntervalRestrictionPval:
    """
    Applies a lower AND upper limit mask to the dataset (inclusive) and discards any data point that is outside of this
    interval.
    This has some extra logic because it is applied to the p-value which is stored as mantissa and exponent, but
    filtered through lower and upper limits that are float.
    """
    def __init__(self, lower, upper, mantissa_dset, exponent_dset):
        self.mantissa_lower = self.mantissa_upper = self.exp_lower = self.exp_upper = None
        if lower is not None and upper is not None:
            if lower > upper:
                raise ValueError("Lower limit must be numerically lower than upper limit!")
        if lower is not None:
            self.mantissa_lower, self.exp_lower = pu.convert_to_mantissa_and_exponent(str(lower))
        if upper is not None:
            self.mantissa_upper, self.exp_upper = pu.convert_to_mantissa_and_exponent(str(upper))

        self.mantissa = mantissa_dset
        self.exponent = exponent_dset

    def get_mask(self):
        """
        Apply 2 filters/masks:
        - one for the p-values that are on the same exponent (order of magnitude) with the limits,
        as these need to take into account the mantissa also
        - one for the p-values that are between the limits and we don't need to take their mantissas into account
        """
        exponent_on_limits = self._mask_for_values_on_exponent_limit()
        exponent_between_limits = self._mask_for_values_between_exponent_limits()
        return logical_or_on_list_of_masks([exponent_on_limits, exponent_between_limits])

    def _mask_for_values_on_exponent_limit(self):
        """
        Filter values that are on the exponent limit (i.e. same order of magnitute) with an equality mask based on
        the exponent value.
        For those that have the same order of magnitude than the upper/lower limits, apply an extra limit based on the
        upper mantissa limit and the lower mantissa limit.
        """
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
        """
        For values that are between the exponent limits, we don't need to take the mantissa into consideration, just
        the exponent value. We do this by streching out the exponent limits by one in both directions
        (we checking between the limits exponents, not on the limits exponents. _mask_for_values_on_exponent_limit takes
        care of that) and then applying an interval mask for those limits.
        """
        mask_between_exp_limits = None
        new_exp_lower = new_exp_upper = None
        if self.exp_lower is not None:
            new_exp_lower = self.exp_lower + 1
        if self.exp_upper is not None:
            new_exp_upper = self.exp_upper - 1
        if (new_exp_lower is not None) and (new_exp_upper is not None):
            if new_exp_lower <= new_exp_upper:
                mask_between_exp_limits = self.exponent.interval_mask(new_exp_lower, new_exp_upper)
        else:
            mask_between_exp_limits = self.exponent.interval_mask(new_exp_lower, new_exp_upper)

        return mask_between_exp_limits


def apply_restrictions(datasets, snp=None, study=None, chromosome=None, pval_interval=None, bp_interval=None):
    """
    This method creates and applies restrictions on datasets. It can not know what restriction we want to apply and
    therefore creates one for each parameter that is passed as an argument and is not None.
    :param datasets: the datasets we want to apply restrictions on
    :param snp: filter for specific SNP
    :param study: filter for specific study accession
    :param chromosome: filter for specific chromosome
    :param pval_interval: filter for specific p-value interval
    :param bp_interval: filter for specific base pair location interval
    :return: the datasets after the restrictions have been performed
    """
    restrictions = [create_simple_restriction(datasets=datasets, datset_name=SNP_DSET, restriction=snp),
                    create_simple_restriction(datasets=datasets, datset_name=STUDY_DSET, restriction=study),
                    create_simple_restriction(datasets=datasets, datset_name=CHR_DSET, restriction=chromosome),
                    create_simple_restriction(datasets=datasets, datset_name=BP_DSET, restriction=bp_interval)]

    restrictions = [restriction for restriction in restrictions if restriction is not None]

    # for p-value filtering we need to create a restriction that will take into account the mantissa and exponent
    # datasets (that store integers) and use a float interval in defining the limits.
    if MANTISSA_DSET in datasets and pval_interval is not None:
        restriction = pval_interval
        dataset_mantissa = datasets[MANTISSA_DSET]
        dataset_exp = datasets[EXP_DSET]
        restrictions.append(get_restriction(restriction, [dataset_mantissa, dataset_exp]))

    # actually apply the restictions to the datasets
    if restrictions:
        return filter_dsets_with_restrictions(datasets, restrictions)

    return datasets


def create_simple_restriction(datasets, datset_name, restriction):
    """
    If the dataset name exists in the datasets directory then create the restriction.
    :param datasets: the directory of datasets
    :param datset_name: the name of the dataset the restriction refers to
    :param restriction: the actual value (or value interval) of the restriction
    :return: a *Restriction object
    """
    if datset_name in datasets and restriction is not None:
        dataset = datasets[datset_name]
        return get_restriction(restriction, dataset)


def get_restriction(restriction, reference_datasets):
    """
    Figures out what type of restriction object to create.
    :param restriction: the actual value (or value interval) of the restriction
    :param reference_datasets: the dataset (or list of datasets) that the restriction is referring to
    :return: the *Restriction object
    """
    if interval.is_interval(restriction):
        if isinstance(reference_datasets, list):
            # interval restriction for p-value examines mantissa and exponent
            if len(reference_datasets) == 2:
                return IntervalRestrictionPval(restriction.floor(), restriction.ceil(), reference_datasets[0], reference_datasets[1])
        else:
            return IntervalRestriction(restriction.floor(), restriction.ceil(), reference_datasets)
    else:
        return EqualityRestriction(restriction, reference_datasets)


def filter_dsets_with_restrictions(datasets, restrictions):
    """
    Takes a list of restrictions and the datasets it wants to apply them to and filters out the data not wanted.
    :param datasets: the directory of the datasets we want to filter
    :param restrictions: a list of *Restriction objects that will be applied
    :return: filtered datasets after applying the restrictions
    """
    # collect the masks of the existing restrictions
    list_of_masks = [restriction.get_mask() for restriction in restrictions if restriction is not None]

    # create one mask from all the masks
    filtering_mask = logical_and_on_list_of_masks(list_of_masks)

    # apply the final mask to all the datasets in the dictonary
    if filtering_mask is not None:
        return utils.filter_dictionary_by_mask(datasets, filtering_mask)

    return datasets


