import pytest
from sumstats.utils.restrictions import *
from sumstats.utils.dataset import Dataset
import sumstats.utils.pval as pu
from sumstats.utils.interval import *
from tests.prep_tests import *
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
        self.loader_dictionary = {SNP_DSET: Dataset(snpsarray), MANTISSA_DSET: Dataset(dataset_mantissa), EXP_DSET: Dataset(dataset_exp),
                     CHR_DSET: Dataset(chrarray), STUDY_DSET: Dataset(studyarray),
                     OR_DSET: Dataset(orarray), BP_DSET: Dataset(bparray),
                EFFECT_DSET: Dataset(effectarray), OTHER_DSET: Dataset(otherarray), FREQ_DSET : Dataset(frequencyarray)}

    def test_interval_restriction_pval_with_lower_bigger_than_upper_limit_raises_error(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        with pytest.raises(AssertionError):
            IntervalRestrictionPval(1.2e-2, 1.3e-10, Dataset(mantissa_array), Dataset(exp_array))

    def test_pvals_with_same_exp_diff_mantissa_out_of_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(1.2e-16, 1.2e-16, Dataset(mantissa_array), Dataset(exp_array))]

        datasets = {MANTISSA_DSET: Dataset(mantissa_array), EXP_DSET: Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(filtered_dsets[MANTISSA_DSET]) == 0
        assert len(filtered_dsets[EXP_DSET]) == 0

    def test_pvals_with_same_exp_diff_mantissa_right_on_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(1.2e-15, 9e-15, Dataset(mantissa_array), Dataset(exp_array))]

        datasets = {MANTISSA_DSET: Dataset(mantissa_array), EXP_DSET: Dataset(exp_array)}
        print(mantissa_array)
        print(exp_array)
        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(filtered_dsets[MANTISSA_DSET]) == 4
        assert len(filtered_dsets[EXP_DSET]) == 4

    def test_pvals_with_same_exp_diff_mantissa_cross_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_exp_diff_mantissa)

        restrictions = [IntervalRestrictionPval(9e-16, 1.2e-14, Dataset(mantissa_array), Dataset(exp_array))]

        datasets = {MANTISSA_DSET: Dataset(mantissa_array), EXP_DSET: Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(filtered_dsets[MANTISSA_DSET]) == 5
        assert len(filtered_dsets[EXP_DSET]) == 5

    def test_pvals_with_same_mantissa_diff_exp_out_of_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_mantissa_diff_exp)

        restrictions = [IntervalRestrictionPval(1.2e-15, 1.2e-15, Dataset(mantissa_array), Dataset(exp_array))]

        datasets = {MANTISSA_DSET: Dataset(mantissa_array), EXP_DSET: Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(filtered_dsets[MANTISSA_DSET]) == 0
        assert len(filtered_dsets[EXP_DSET]) == 0

    def test_pvals_with_same_mantissa_diff_exp_right_on_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_mantissa_diff_exp)

        restrictions = [IntervalRestrictionPval(1.2e-10, 1.2e-1, Dataset(mantissa_array), Dataset(exp_array))]
        datasets = {MANTISSA_DSET: Dataset(mantissa_array), EXP_DSET: Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(filtered_dsets[MANTISSA_DSET]) == 8
        assert len(filtered_dsets[EXP_DSET]) == 8

    def test_pvals_with_same_mantissa_diff_exp_cross_on_limits(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals_same_mantissa_diff_exp)

        restrictions = [IntervalRestrictionPval(1.2e-9, 1.2e-2, Dataset(mantissa_array), Dataset(exp_array))]
        datasets = {MANTISSA_DSET: Dataset(mantissa_array), EXP_DSET: Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(filtered_dsets[MANTISSA_DSET]) == 5
        assert len(filtered_dsets[EXP_DSET]) == 5

    def test_various_pvals_1(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals)

        restrictions = [IntervalRestrictionPval(5e-9, 5e-9, Dataset(mantissa_array), Dataset(exp_array))]
        datasets = {MANTISSA_DSET: Dataset(mantissa_array), EXP_DSET: Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(filtered_dsets[MANTISSA_DSET]) == 1
        assert len(filtered_dsets[EXP_DSET]) == 1
        assert filtered_dsets[MANTISSA_DSET][0] == 5
        assert filtered_dsets[EXP_DSET][0] == -9

    def test_various_pvals_2(self):
        mantissa_array, exp_array = get_mantissa_and_exp_arrays_from_pvals(pvals)

        restrictions = [IntervalRestrictionPval(4e-9, 5e-3, Dataset(mantissa_array), Dataset(exp_array))]
        datasets = {MANTISSA_DSET: Dataset(mantissa_array), EXP_DSET: Dataset(exp_array)}

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(filtered_dsets[MANTISSA_DSET]) == 3
        assert len(filtered_dsets[EXP_DSET]) == 3

    def test_filter_dsets_with_restrictions(self):
        datasets = {SNP_DSET: Dataset(["rs1", "rs1", "rs1", "rs2", "rs3"]), PVAL_DSET: Dataset([1., 2.1, 3, 3.1, 4]),
                           CHR_DSET: Dataset([1, 1, 1, 1, 2])}

        restrictions = [EqualityRestriction("rs1", datasets[SNP_DSET]),
                        IntervalRestriction(1., 2.1, datasets[PVAL_DSET]),
                        EqualityRestriction(1, datasets[CHR_DSET])]

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)

        assert len(list(filtered_dsets.keys())) == 3

        assert len(filtered_dsets[SNP_DSET]) == 2
        assert len(set(filtered_dsets[SNP_DSET])) == 1
        assert filtered_dsets[SNP_DSET][0] == "rs1"

        assert len(filtered_dsets[PVAL_DSET]) == 2
        for pval in filtered_dsets[PVAL_DSET]:
            assert pval >= 1.
            assert pval <= 2.1

        assert len(filtered_dsets[CHR_DSET]) == 2
        for chromosome in filtered_dsets[CHR_DSET]:
            assert chromosome == 1

        restrictions = [IntervalRestriction(3., 3.1, datasets[PVAL_DSET]),
                        EqualityRestriction(1, datasets[CHR_DSET])]

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(list(filtered_dsets.keys())) == 3
        assert len(filtered_dsets[SNP_DSET]) == 2

        assert filtered_dsets[SNP_DSET][0] == "rs1"
        assert filtered_dsets[SNP_DSET][1] == "rs2"

        assert len(filtered_dsets[PVAL_DSET]) == 2
        for pval in filtered_dsets[PVAL_DSET]:
            assert pval >= 3.
            assert pval <= 3.1

        assert len(filtered_dsets[CHR_DSET]) == 2
        for chromosome in filtered_dsets[CHR_DSET]:
            assert chromosome == 1

        restrictions = [IntervalRestriction(4., 4., datasets[PVAL_DSET]), ]

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(list(filtered_dsets.keys())) == 3
        assert len(filtered_dsets[SNP_DSET]) == 1

        assert filtered_dsets[SNP_DSET][0] == "rs3"

        assert len(filtered_dsets[PVAL_DSET]) == 1
        assert filtered_dsets[PVAL_DSET][0] == 4.

        assert len(filtered_dsets[CHR_DSET]) == 1
        assert filtered_dsets[CHR_DSET][0] == 2

        #
        restrictions = []

        filtered_dsets = filter_dsets_with_restrictions(datasets, restrictions)
        assert len(list(filtered_dsets.keys())) == 3
        for dset_name in datasets:
            assert len(datasets[dset_name]) == 5

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
        datasets = self.loader_dictionary

        filtered_dsets = apply_restrictions(datasets)
        for name, dataset in filtered_dsets.items():
            assert np.array_equal(dataset, datasets[name])

    def test_apply_snp_restriction(self):
        datasets = self.loader_dictionary

        filtered_dsets = apply_restrictions(datasets, 'rs185339560')

        for dataset in filtered_dsets.values():
            assert len(dataset) == 1

    def test_apply_pval_restriction(self):
        datasets = self.loader_dictionary
        # snpsarray = ["rs185339560", "rs11250701", "rs12345", "rs7085086"]
        # pvalsarray = ["0.4865", "0.4314", "0.5986", "0.07057"]
        filtered_dsets = apply_restrictions(datasets, pval_interval=FloatInterval().set_string_tuple("9e-3:0.44"))

        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 2

    def test_apply_study_restriction(self):
        datasets = self.loader_dictionary

        filtered_dsets = apply_restrictions(datasets, study="PM001")
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 2

    def test_apply_study_and_snp_restriction(self):
        datasets = self.loader_dictionary

        filtered_dsets = apply_restrictions(datasets, study="PM001", snp="rs185339560")
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 1

    def test_apply_chr_restriction(self):
        datasets = self.loader_dictionary

        filtered_dsets = apply_restrictions(datasets, chromosome=1)
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 2

    def test_apply_bp_restriction(self):
        datasets = self.loader_dictionary
        # bparray = [1118275, 1120431, 49129966, 48480252]
        filtered_dsets = apply_restrictions(datasets, bp_interval=IntInterval().set_string_tuple("1118275:1218275"))
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 2

    def test_apply_study_and_pval_restriction(self):
        datasets = self.loader_dictionary
        print(datasets)
        # pvalsarray = ["0.4865", "0.4314", "0.5986", "0.07057"]
        filtered_dsets = apply_restrictions(datasets, pval_interval=FloatInterval().set_string_tuple("9e-3:0.44"),
                                            study="PM002")
        print(filtered_dsets)
        for name, dataset in filtered_dsets.items():
            assert len(dataset) == 1

