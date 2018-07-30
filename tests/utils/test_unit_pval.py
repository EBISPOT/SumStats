import sumstats.utils.pval as pu
import pytest
import numpy as np


class TestUnitPval(object):
    def test__num_of_zeros_preceding(self):
        str_number = "1"
        assert pu._num_of_zeros_preceding(str_number) == 0

        str_number = "0"
        assert pu._num_of_zeros_preceding(str_number) == 1

        str_number = "00"
        assert pu._num_of_zeros_preceding(str_number) == 2

        str_number = "00100"
        assert pu._num_of_zeros_preceding(str_number) == 2

        str_number = "10"
        assert pu._num_of_zeros_preceding(str_number) == 0

    def test__split_decimal(self):
        str_number = "0"
        with pytest.raises(AssertionError):
            pu._split_decimal(str_number)

        str_number = "1"
        with pytest.raises(AssertionError):
            pu._split_decimal(str_number)

        str_number = "1,0"
        with pytest.raises(AssertionError):
            pu._split_decimal(str_number)

        str_number = "1."
        whole, dec = pu._split_decimal(str_number)
        assert whole == "1"
        assert dec == 0

        str_number = "1.0"
        whole, dec = pu._split_decimal(str_number)
        assert whole == "1"
        assert dec == "0"

        str_number = "0.1"
        whole, dec = pu._split_decimal(str_number)
        assert whole == "0"
        assert dec == "1"

    def test_is_exponent_form(self):
        str_number = "0"
        assert not pu._is_exponent_form(str_number)

        str_number = "0e"
        assert pu._is_exponent_form(str_number)

        str_number = "0E"
        assert pu._is_exponent_form(str_number)

    def test_is_decimal_form(self):
        str_number = "0,0"
        assert not pu._is_decimal_form(str_number)

        str_number = "1"
        assert not pu._is_decimal_form(str_number)

        str_number = "1.0"
        assert pu._is_decimal_form(str_number)

    def test_format_fractional_part(self):
        fractional_part = "00991"
        mantissa, exp = pu._format_fractional_part(fractional_part)
        assert mantissa == 9.91
        assert exp == -3

        fractional_part = "991"
        mantissa, exp = pu._format_fractional_part(fractional_part)
        assert mantissa == 9.91
        assert exp == -1

        fractional_part = "9910000"
        mantissa, exp = pu._format_fractional_part(fractional_part)
        assert mantissa == 9.91
        assert exp == -1

        fractional_part = "991999999988979798349823987429873489709092309409234092309402934092340923094029340923409234234987234987239847239874 "
        mantissa, exp = pu._format_fractional_part(fractional_part)
        assert mantissa == 9.91999999988979798349823987429873489709092309409234092309402934092340923094029340923409234234987234987239847239874
        assert exp == -1

    def test_format_decimal(self):
        str_number = "0.445034512842"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 4.45034512842
        assert exp == -1

        str_number = "0.000197968259869"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 1.97968259869
        assert exp == -4

        str_number = "0.00154564078624"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 1.54564078624
        assert exp == -3

        str_number = "0.0019999999999900"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 1.99999999999
        assert exp == -3

        str_number = "0."
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 0
        assert exp == 0

        str_number = "1.2"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 1.2
        assert exp == 0

        str_number = "1.0"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 1.
        assert exp == 0

        str_number = "0.2"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 2.
        assert exp == -1

        str_number = "0.002"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 2.
        assert exp == -3

        str_number = "0.0002"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 2.
        assert exp == -4

        str_number = "12.2"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 12.2
        assert exp == 0

        str_number = "00.11"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 1.1
        assert exp == -1

        str_number = "0.01"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 1.
        assert exp == -2

        str_number = "1."
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 1.
        assert exp == 0

        str_number = "0.00"
        mantissa, exp = pu._format_decimal(str_number)
        assert mantissa == 0
        assert exp == 0

    def test_format_existing_e(self):
        str_number = "5.42697191122e-07"
        mantissa, exp = pu._format_existing_e(str_number)
        assert mantissa == 5.42697191122
        assert exp == -7

        str_number = "5.454699579020e-7"
        mantissa, exp = pu._format_existing_e(str_number)
        assert mantissa == 5.454699579020
        assert exp == -7

        str_number = "6.29351382088e-06"
        mantissa, exp = pu._format_existing_e(str_number)
        assert mantissa == 6.29351382088
        assert exp == -6

        str_number = "1e-456789"
        mantissa, exp = pu._format_existing_e(str_number)
        assert mantissa == 1
        assert exp == -456789

        str_number = "0.1e-456789"
        mantissa, exp = pu._format_existing_e(str_number)
        assert mantissa == 0.1
        assert exp == -456789

        str_number = "0E-456789"
        mantissa, exp = pu._format_existing_e(str_number)
        assert mantissa == 0
        assert exp == -456789

        str_number = "0.E-456789"
        mantissa, exp = pu._format_existing_e(str_number)
        assert mantissa == 0
        assert exp == -456789

        str_number = "5.42697191122a-07"
        with pytest.raises(ValueError):
            pu._format_existing_e(str_number)

        str_number = "0.0001"
        with pytest.raises(ValueError):
            pu._format_existing_e(str_number)

        str_number = "e-45"
        with pytest.raises(ValueError):
            pu._format_existing_e(str_number)

        str_number = "1e"
        with pytest.raises(ValueError):
            pu._format_existing_e(str_number)

    def test_convert_to_mantissa_and_exponent(self):
        str_number = "0"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 0
        assert exp == 0

        str_number = "1"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 1
        assert exp == 0

        str_number = "123"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 123
        assert exp == 0

        str_number = "123.1"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 123.1
        assert exp == 0

        str_number = "1.982892734897234897234E-7891234"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 1.982892734897234897234
        assert exp == -7891234

        str_number = "1.01e-098"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 1.01
        assert exp == -98

        str_number = "1.01e-0980"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 1.01
        assert exp == -980

        str_number = "1.01E-0980"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 1.01
        assert exp == -980

        str_number = "1.01E+0980"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 1.01
        assert exp == 980

        str_number = "1.01e+0980"
        mantissa, exp = pu.convert_to_mantissa_and_exponent(str_number)
        assert mantissa == 1.01
        assert exp == 980

    def test_pval_without_zero_before_point(self):
            str_number = ".1"
            whole, dec = pu._split_decimal(str_number)
            assert whole == 0
            assert dec == "1"

    def test_get_mantissa_and_exp_lists(self):
        list_of_strings = ['1.2', '0.1', '0.0', '0.002', '0.8e-10', '8E-10']
        mantissa_list, exp_list = pu.get_mantissa_and_exp_lists(list_of_strings)

        assert mantissa_list is not None
        assert len(mantissa_list) == len(list_of_strings)
        assert np.array_equal(mantissa_list, [1.2, 1., 0., 2., 0.8, 8.])

        assert exp_list is not None
        assert len(exp_list) == len(list_of_strings)
        assert np.array_equal(exp_list, [0, -1, 0, -3, -10, -10])

        list_of_strings = ['1,2']
        with pytest.raises(ValueError):
            pu.get_mantissa_and_exp_lists(list_of_strings)

        list_of_strings = [1.2]
        with pytest.raises(TypeError):
            pu.get_mantissa_and_exp_lists(list_of_strings)

        list_of_strings = [1]
        with pytest.raises(TypeError):
            pu.get_mantissa_and_exp_lists(list_of_strings)