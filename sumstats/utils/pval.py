"""
This module contains a set of methods to take a float represented
in as a string, and extract it's mantissa and exponent
without loosing information
"""


def _split_decimal(str_numer):
    assert _is_decimal_form(str_numer), "To split a decimal, it need to be a decimal!"
    integer_part, fractional_part = str_numer.split(".")
    if integer_part == "":
        integer_part = 0
    if fractional_part == "":
        fractional_part = 0
    return integer_part, fractional_part


def _is_exponent_form(str_number):
    return "e" in str_number or "E" in str_number


def _is_decimal_form(str_number):
    return "." in str_number


def _num_of_zeros_preceding(str_number):
    zeros = 0
    for char in str_number:
        if char == "0":
            zeros += 1
        else:
            break
    return zeros


def _format_fractional_part(fractional_part):
    zeros = _num_of_zeros_preceding(fractional_part)
    fractional_part = fractional_part.strip("0")
    exp = -(zeros + 1)
    mantissa = fractional_part[0] + "." + "".join(fractional_part[1:])
    return float(mantissa), exp


def _format_decimal(str_number):
    integer_part, fractional_part = _split_decimal(str_number)
    if int(integer_part) == 0:
        if int(fractional_part) == 0:
            return 0, 0
        return _format_fractional_part(fractional_part)

    mantissa = float(str_number)
    exp = 0
    return mantissa, exp


def _format_existing_e(str_number):
    if "e" in str_number:
         mantissa = str_number.split('e')[0]
         exp = str_number.split('e')[1]
    elif "E" in str_number:
        mantissa = str_number.split('E')[0]
        exp = str_number.split('E')[1]
    else:
        raise ValueError("Exponent form doesn't have e or E!")
    return float(mantissa), int(exp)


def convert_to_mantissa_and_exponent(str_number):
    if _is_exponent_form(str_number):
        return _format_existing_e(str_number)
    elif _is_decimal_form(str_number):
        return _format_decimal(str_number)

    mantissa = float(str_number)
    exp = 0
    return mantissa, exp


def get_mantissa_and_exp_lists(string_list):
    mantissa_dset = []
    exp_dset = []
    for str_number in string_list:
        mantissa, exp = convert_to_mantissa_and_exponent(str_number)
        mantissa_dset.append(mantissa)
        exp_dset.append(exp)

    return mantissa_dset, exp_dset



