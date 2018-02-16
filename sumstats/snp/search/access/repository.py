"""
Utils useful for querying
"""

from sumstats.snp.constants import *


def get_dsets_from_group(group, start, size):
    return group.load_datasets(dset_names=TO_QUERY_DSETS, start=start, size=size)
