
def cutoff_mask(vector, upper_limit, lower_limit):
    mask_u = get_upper_limit_mask(upper_limit, vector)
    mask_l = get_lower_limit_mask(lower_limit, vector)
    return combine_masks(mask_u, mask_l)


def combine_masks(mask1, mask2):
    if mask1 is None:
        return mask2
    if mask2 is None:
        return mask1
    return [all(tup) for tup in zip(mask1, mask2)]


def get_upper_limit_mask(upper_limit, vector):
    mask = None
    if upper_limit is not None:
        mask = vector <= upper_limit
    return mask


def get_lower_limit_mask(lower_limit, vector):
    mask = None
    if lower_limit is not None:
        mask = vector >= lower_limit
    return mask


def get_equality_mask(value, vector):
    mask = None
    if value is not None:
        mask = vector == value

    return mask


def filter_dictionary_by_mask(dictionary, mask):
    for dset in dictionary:
        dictionary[dset] = filter_by_mask(dictionary[dset], mask)

    return dictionary


def filter_by_mask(vector, mask):
    return vector[mask]


def get_group_from_parent(parent_group, child_group):
    group = parent_group.get(str(child_group))
    if group is None:
        print "%s does not exist in %s" % (child_group, parent_group)
        raise SystemExit(1)
    return group


def get_dset(group, dset_name):
    dset = group.get(dset_name)
    if dset is not None:
        dset = dset[:]
    return dset