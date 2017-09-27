import h5py


def same_digits(list1, list2):
    same = True
    for i in range(1, len(list2)):
        if list1[i] != list2[i]:
            same = False
            break
    return same


def fitting_block_size(block_size, bp):
    i = block_size
    while i < bp + block_size and bp >= i:
        i += block_size
    return i


def to_list_of_ints(number):
    list = []
    for digit in str(number):
        list.append(int(digit))
    return list


def get_block_from_bp(block_size, bp):
    str_block = to_list_of_ints(block_size)
    block_digits = len(str_block)

    str_bp = to_list_of_ints(bp)
    digits = len(str_bp)

    if bp == block_size:
        print block_size

    elif digits < block_digits:
        print block_size

    elif digits == block_digits:
        if str_bp[0] == str_block[0]:
            # we are here, it is not == block size because if it was then we would have caught that already
            # we are just above the first block size, so we are in the second block
            return 2 * block_size
        else:
            # check if all the other digits match (except the first one), and if so then return bp as the block
            # if the digits do not match then give back the next block

            # loop through the rest of the digits

            same = same_digits(str_bp, str_block)
            if same:
                return bp
            else:
                correct_block = fitting_block_size(block_size, bp)
                return correct_block
    else:
        # bp digits are bigger than block digits
        # this means that we should keep the last x digits of bp
        # where x is the number of digits in block_size
        # if they are the same then we can again return bp
        # if they are not the same we need to return the last digits + block_size, and
        # keep the first digits as they are
        # example block size = 100
        # if bp = 1100 return bp
        # if bp = 1101 return 1200
        last_bp_digits = str_bp[::-1][0:block_digits][::-1]
        same = same_digits(last_bp_digits, str_block)
        if same:
            return bp
        else:
            first_bp_digits = str_bp[::-1][block_digits:][::-1]
            last_bp_digits_as_int = int("".join(str(x) for x in last_bp_digits))

            correct_sub_block = fitting_block_size(block_size, last_bp_digits_as_int)

            first_bp_digits_str = "".join(str(x) for x in first_bp_digits)
            correct_block = int(first_bp_digits_str + str(correct_sub_block))
            return correct_block


def my_print(x, y):
    print x, y


def print_items_of_file(file):
    f = h5py.File(file, 'r')
    f.visititems(my_print)
