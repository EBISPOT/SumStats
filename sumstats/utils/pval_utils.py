
def _split_decimal(str_numer):
    assert _is_decimal_form(str_numer), "To split a decimal, it need to be a decimal!"
    dot_split = str_numer.split(".")
    if dot_split[1] == "":
        return dot_split[0], 0
    return dot_split[0], dot_split[1]


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


