"""
Utils useful for querying
"""

from sumstats.chr.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def get_block_groups_from_parent_within_block_range(chr_group, bp_interval):
    """
    block_lower and block_upper should be concrete blocks (i.e. factor of the block_size)
    for block size 100, when I say I want block 100-200 I need to get back block groups[100, 200]
     (i.e. all the positions from 0-200)
    """
    if (bp_interval.floor() % BLOCK_SIZE != 0) or (bp_interval.ceil() % BLOCK_SIZE != 0):
        raise ValueError(
            "block sizes not conforming to the block size: %s, block_lower: %ds(s), block_upper: %ds(s)" % (
                BLOCK_SIZE, bp_interval.floor(), bp_interval.ceil()))
    if bp_interval.floor() > bp_interval.ceil():
        raise ValueError("lower limit is bigger than upper limit")

    blocks = [gu.get_group_from_parent(chr_group, block) for block in
              range(bp_interval.floor(), (bp_interval.ceil() + BLOCK_SIZE), BLOCK_SIZE)]
    return blocks


def get_dsets_from_plethora_of_blocks(groups, start, size):
    dict_groups = {group: group for group in groups}
    return get_dsets_from_parent_group(groups, start, size)


def get_dsets_from_group(group, start, size):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    return gu.extend_dsets_for_group(group=group, name_to_dataset=name_to_dataset, start=start, size=size)


def get_block_number(bp_position):
    """
    Calculates the block that this BP (base pair location) will belong
    Blocks are saved with their upper limit, i.e. for block size = 100 if
    bp == 50 then it is saved in the block 0-100, so we will get back
    the block name called "100"

    :param bp_position: the base pair location
    :return: the upper limit of the block that the bp belongs to
    """

    if bp_position <= BLOCK_SIZE:
        return BLOCK_SIZE
    else:
        is_factor_of_block_size = bp_position % BLOCK_SIZE == 0
        if is_factor_of_block_size:
            return bp_position
        else:
            return bp_position - (bp_position % BLOCK_SIZE) + BLOCK_SIZE


def get_dsets_from_parent_group(group, start, size):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

    end = start + size
    if isinstance(group, h5py._hl.group.Group):
        for child_group_name, child_group in group.items():
            dset_size = get_standard_group_dset_size(child_group)
            if group_has_groups(child_group):
                name_to_dataset = get_dsets_from_parent_group(child_group, start, size)
                dset_size = len(name_to_dataset[MANTISSA_DSET])

            if continue_to_next_group(start, dset_size):
                continue
            else:
                subset_of_datasets = get_dsets_from_group(child_group, start, size)
                name_to_dataset = extend_dsets_with_subset(name_to_dataset, subset_of_datasets)

                if end <= dset_size:
                    return name_to_dataset
                else:
                    size = calculate_remaining_size_from_data_subset(size, subset_of_datasets)
                    continue
        return name_to_dataset
    else:
        for child_group in group:
            dset_size = get_standard_group_dset_size(child_group)
            if group_has_groups(child_group):
                name_to_dataset = get_dsets_from_parent_group(child_group, start, size)
                dset_size = len(name_to_dataset[MANTISSA_DSET])

            if continue_to_next_group(start, dset_size):
                print("next group")
                continue
            else:
                subset_of_datasets = get_dsets_from_group(child_group, start, size)
                name_to_dataset = extend_dsets_with_subset(name_to_dataset, subset_of_datasets)

                if end <= dset_size:
                    return name_to_dataset
                else:
                    size = calculate_remaining_size_from_data_subset(size, subset_of_datasets)
                    continue
        return name_to_dataset


def get_standard_group_dset_size(group):
    if MANTISSA_DSET in group:
        return group.get(MANTISSA_DSET).shape[0]
    else:
        return 0


def group_has_groups(group):
    if isinstance(group, h5py._hl.group.Group):
        for name, item in group.items():
            return isinstance(item, h5py._hl.group.Group)
    else:
        return False


def continue_to_next_group(start, dset_size):
    return start >= dset_size


def extend_dsets_with_subset(name_to_dataset, subset):
    for dset_name, dataset in name_to_dataset.items():
        dataset.extend(subset[dset_name])
    return name_to_dataset


def calculate_remaining_size_from_data_subset(size, subset):
    retrieved_size = len(subset[MANTISSA_DSET])
    size = size - retrieved_size
    return size
