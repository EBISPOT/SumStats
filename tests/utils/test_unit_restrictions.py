import os
import h5py
import pytest
from sumstats.utils.restrictions import *
import sumstats.utils.utils as utils
from sumstats.utils.dataset import Dataset
import sumstats.utils.pval as pu


pvals_same_exp_diff_mantissa = ["0.0000000000000013", "0.0000000000000012", "0.0000000000000011", "0.000000000000009", "1.5e-15"]
pvals_same_mantissa_diff_exp = ["1.2e0", "1.2e-0", "1.2e-0", "1.2e0", "1.2e-1", "1.2e1", "1.2e-9", "1.2e0"]


class TestUnitUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_interval_restriction_pval_with_lower_bigger_than_upper_limit_raises_error(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        with pytest.raises(AssertionError):
            IntervalRestrictionPval(1.2e-2, 1.3e-10, Dataset(mantissa_array), Dataset(exp_array))

    def test_pvals_with_same_exp_diff_mantissa_out_of_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        print(mantissa_array, exp_array, pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(1.2e-16, 1.2e-16, Dataset(mantissa_array), Dataset(exp_array))]

        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 0
        assert len(filtered_dsets['exp']) == 0

    def test_pvals_with_same_exp_diff_mantissa_right_on_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        print(mantissa_array, exp_array, pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(1.2e-15, 9e-15, Dataset(mantissa_array), Dataset(exp_array))]

        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 4
        assert len(filtered_dsets['exp']) == 4

    def test_pvals_with_same_exp_diff_mantissa_cross_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        print(mantissa_array, exp_array, pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(9e-16, 1.2e-14, Dataset(mantissa_array), Dataset(exp_array))]

        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 5
        assert len(filtered_dsets['exp']) == 5

    def test_pvals_with_same_mantissa_diff_exp_out_of_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_mantissa_diff_exp)

        print(mantissa_array, exp_array, pvals_same_mantissa_diff_exp)

        restrictions = [IntervalRestrictionPval(1.2e-15, 1.2e-15, Dataset(mantissa_array), Dataset(exp_array))]

        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 0
        assert len(filtered_dsets['exp']) == 0

    def test_pvals_with_same_mantissa_diff_exp_right_on_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_mantissa_diff_exp)

        print(mantissa_array, exp_array, pvals_same_mantissa_diff_exp)

        restrictions = [IntervalRestrictionPval(1.2e-10, 1.2e1, Dataset(mantissa_array), Dataset(exp_array))]
        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = utils.filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 8
        assert len(filtered_dsets['exp']) == 8


def get_mantissa_and_exp_arrays_from_pvals(array_of_pvals):
    mantissa_array = []
    exp_array = []
    for pval in array_of_pvals:
        mantissa, exponent = pu.convert_to_mantissa_and_exponent(pval)
        mantissa_array.append(mantissa)
        exp_array.append(exponent)
    return mantissa_array, exp_array
