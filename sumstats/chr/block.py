from sumstats.chr.constants import *
from sumstats.utils.interval import *


def fill_in_block_limits(bp_interval):
    floor = bp_interval.floor()
    ceil = bp_interval.ceil()
    if floor is None:
        return IntInterval().set_tuple(ceil, ceil)
    elif ceil is None:
        return IntInterval().set_tuple(floor, floor)
    else:
        return bp_interval


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


class Block:

    def __init__(self, bp_interval):
        bp_interval = fill_in_block_limits(bp_interval)
        self.ceil = bp_interval.ceil()
        self.floor = bp_interval.floor()

        self.ceil_block = get_block_number(self.ceil)
        self.floor_block = get_block_number(self.floor)

    def get_block_groups_from_parent(self, parent_group):
        """
        block_lower and block_upper should be concrete blocks (i.e. factor of the block_size)
        for block size 100, when I say I want block 100-200 I need to get back block groups[100, 200]
         (i.e. all the positions from 0-200)
        """
        if self.floor_block > self.ceil_block:
            raise ValueError("lower limit is bigger than upper limit")

        blocks = (parent_group.get_subgroup(block) for block in
                  range(self.floor_block, (self.ceil_block + BLOCK_SIZE), BLOCK_SIZE) if
                  parent_group.subgroup_exists(block))

        return blocks