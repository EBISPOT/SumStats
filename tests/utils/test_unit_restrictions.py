import pytest
from sumstats.utils.restrictions import *
from sumstats.utils.dataset import Dataset
import sumstats.utils.pval as pu
from sumstats.utils.interval import *
from tests.utils.test_constants import *
import numpy as np


pvals_same_exp_diff_mantissa = ["0.0000000000000013", "0.0000000000000012", "0.0000000000000011", "0.000000000000009", "1.5e-15"]
pvals_same_mantissa_diff_exp = ["1.2e-10", "1.2e-1", "1.2e-1", "1.2e-2", "1.2e-3", "1.2e-4", "1.2e-9", "1.2e-9"]
pvals = ["2e-10", "3e-9", "1e-9", "1e-11", "6e-2", "5e-3", "6e-3", "5e-4", "5e-9"]

def get_mantissa_and_exp_arrays_from_pvals(array_of_pvals):
    mantissa_array = []
    exp_array = []
    for pval in array_of_pvals:
        mantissa, exponent = pu.convert_to_mantissa_and_exponent(pval)
        mantissa_array.append(mantissa)
        exp_array.append(exponent)
    return mantissa_array, exp_array


class TestUnitUtils(object):

    def setup_method(self, method):

        dataset_mantissa, dataset_exp = get_mantissa_and_exp_arrays_from_pvals(pvalsarray)
        self.dict = {"snp": Dataset(snpsarray), "mantissa": Dataset(dataset_mantissa), "exp": Dataset(dataset_exp),
                     "chr": Dataset(chrarray), "study": Dataset(studyarray),
                     "or": Dataset(orarray), "bp": Dataset(bparray),
                "effect": Dataset(effectarray), "other": Dataset(otherarray), 'freq' : Dataset(frequencyarray)}

    def test_interval_restriction_pval_with_lower_bigger_than_upper_limit_raises_error(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        with pytest.raises(AssertionError):
            IntervalRestrictionPval(1.2e-2, 1.3e-10, Dataset(mantissa_array), Dataset(exp_array))

    def test_pvals_with_same_exp_diff_mantissa_out_of_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(1.2e-16, 1.2e-16, Dataset(mantissa_array), Dataset(exp_array))]

        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 0
        assert len(filtered_dsets['exp']) == 0

    def test_pvals_with_same_exp_diff_mantissa_right_on_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(1.2e-15, 9e-15, Dataset(mantissa_array), Dataset(exp_array))]

        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}
        print(mantissa_array)
        print(exp_array)
        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 4
        assert len(filtered_dsets['exp']) == 4

    def test_pvals_with_same_exp_diff_mantissa_cross_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(9e-16, 1.2e-14, Dataset(mantissa_array), Dataset(exp_array))]

        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 5
        assert len(filtered_dsets['exp']) == 5

    def test_pvals_with_same_mantissa_diff_exp_out_of_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_mantissa_diff_exp)

        restrictions = [IntervalRestrictionPval(1.2e-15, 1.2e-15, Dataset(mantissa_array), Dataset(exp_array))]

        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 0
        assert len(filtered_dsets['exp']) == 0

    def test_pvals_with_same_mantissa_diff_exp_right_on_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_mantissa_diff_exp)

        restrictions = [IntervalRestrictionPval(1.2e-10, 1.2e-1, Dataset(mantissa_array), Dataset(exp_array))]
        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 8
        assert len(filtered_dsets['exp']) == 8

    def test_pvals_with_same_mantissa_diff_exp_cross_on_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_mantissa_diff_exp)

        restrictions = [IntervalRestrictionPval(1.2e-9, 1.2e-2, Dataset(mantissa_array), Dataset(exp_array))]
        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 5
        assert len(filtered_dsets['exp']) == 5

    def test_various_pvals_1(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals)

        restrictions = [IntervalRestrictionPval(5e-9, 5e-9, Dataset(mantissa_array), Dataset(exp_array))]
        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 1
        assert len(filtered_dsets['exp']) == 1
        assert filtered_dsets['mantissa'][0] == 5
        assert filtered_dsets['exp'][0] == -9

    def test_various_pvals_2(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals)

        restrictions = [IntervalRestrictionPval(4e-9, 5e-3, Dataset(mantissa_array), Dataset(exp_array))]
        name_to_dataset = {'mantissa': Dataset(mantissa_array), 'exp': Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(filtered_dsets['mantissa']) == 3
        assert len(filtered_dsets['exp']) == 3

    def test_filter_dsets_with_restrictions(self):
        name_to_dataset = {'snp': Dataset(["rs1", "rs1", "rs1", "rs2", "rs3"]), 'pval': Dataset([1., 2.1, 3, 3.1, 4]),
                           'chr': Dataset([1, 1, 1, 1, 2])}

        restrictions = [EqualityRestriction("rs1", name_to_dataset["snp"]),
                        IntervalRestriction(1., 2.1, name_to_dataset["pval"]),
                        EqualityRestriction(1, name_to_dataset["chr"])]

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)

        assert len(list(filtered_dsets.keys())) == 3

        assert len(filtered_dsets['snp']) == 2
        assert len(set(filtered_dsets['snp'])) == 1
        assert filtered_dsets['snp'][0] == "rs1"

        assert len(filtered_dsets['pval']) == 2
        for pval in filtered_dsets['pval']:
            assert pval >= 1.
            assert pval <= 2.1

        assert len(filtered_dsets['chr']) == 2
        for chr in filtered_dsets['chr']:
            assert chr == 1

        restrictions = [IntervalRestriction(3., 3.1, name_to_dataset["pval"]),
                        EqualityRestriction(1, name_to_dataset["chr"])]

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(list(filtered_dsets.keys())) == 3
        assert len(filtered_dsets['snp']) == 2

        assert filtered_dsets['snp'][0] == "rs1"
        assert filtered_dsets['snp'][1] == "rs2"

        assert len(filtered_dsets['pval']) == 2
        for pval in filtered_dsets['pval']:
            assert pval >= 3.
            assert pval <= 3.1

        assert len(filtered_dsets['chr']) == 2
        for chr in filtered_dsets['chr']:
            assert chr == 1

        restrictions = [IntervalRestriction(4., 4., name_to_dataset["pval"]), ]

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(list(filtered_dsets.keys())) == 3
        assert len(filtered_dsets['snp']) == 1

        assert filtered_dsets['snp'][0] == "rs3"

        assert len(filtered_dsets['pval']) == 1
        assert filtered_dsets['pval'][0] == 4.

        assert len(filtered_dsets['chr']) == 1
        assert filtered_dsets['chr'][0] == 2

        #
        restrictions = []

        filtered_dsets = filter_dsets_with_restrictions(name_to_dataset, restrictions)
        assert len(list(filtered_dsets.keys())) == 3
        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 5

    def test_get_equality_int_restriction(self):
        dataset_float = Dataset([1., 2., 3.])

        restriction = get_restriction(1., dataset_float)
        assert isinstance(restriction, EqualityRestriction)

    def test_get_float_restriction(self):
        dataset_float = Dataset([1., 2., 3.])

        restriction = get_restriction(FloatInterval().set_string_tuple("1.:2."), dataset_float)
        assert isinstance(restriction, IntervalRestriction)

    def test_get_equality_str_restriction(self):
        dataset_str = Dataset(['rs1', 'rs2', 'rs3'])

        restriction = get_restriction('rs1', dataset_str)
        assert isinstance(restriction, EqualityRestriction)

    def test_get_interval_pval_restriction(self):
        dataset_mantissa = Dataset([1, 12, 13])
        dataset_exp = Dataset([-1, -2 ,-3])

        restriction = get_restriction(FloatInterval().set_string_tuple("1e-3:1e-2"), [dataset_mantissa, dataset_exp])
        assert isinstance(restriction, IntervalRestrictionPval)

    def test_apply_no_restriction(self):
        name_to_dataset = self.dict

        filtered_dsets = apply_restrictions(name_to_dataset)
        for name, dataset in filtered_dsets.items():
            assert np.array_equal(dataset, name_to_dataset[name])

    def test_apply_snp_restriction(self):
        name_to_dataset = self.dict

        filtered_dsets = apply_restrictions(name_to_dataset, 'rs185339560')

        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 1

    def test_apply_pval_restriction(self):
        name_to_dset = self.dict
        # pvalsarray = ["0.4865", "0.4314", "0.5986", "0.07057"]
        filtered_dsets = apply_restrictions(name_to_dset, pval_interval=FloatInterval().set_string_tuple("9e-3:0.44"))

        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 2

    def test_apply_study_restriction(self):
        name_to_dset = self.dict

        filtered_dsets = apply_restrictions(name_to_dset, study="PM001")
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 2

    def test_apply_study_and_snp_restriction(self):
        name_to_dset = self.dict

        filtered_dsets = apply_restrictions(name_to_dset, study="PM001", snp="rs185339560")
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 1

    def test_apply_chr_restriction(self):
        name_to_dset = self.dict

        filtered_dsets = apply_restrictions(name_to_dset, chr=1)
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 2

    def test_apply_bp_restriction(self):
        name_to_dset = self.dict
        # bparray = [1118275, 1120431, 49129966, 48480252]
        filtered_dsets = apply_restrictions(name_to_dset, bp_interval=IntInterval().set_string_tuple("1118275:1218275"))
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 2

    def test_apply_study_and_pval_restriction(self):
        name_to_dset = self.dict
        # bparray = [1118275, 1120431, 49129966, 48480252]
        # pvalsarray = ["0.4865", "0.4314", "0.5986", "0.07057"]
        filtered_dsets = apply_restrictions(name_to_dset, pval_interval=FloatInterval().set_string_tuple("9e-3:0.44"),
                                            study="PM002")

        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 1

