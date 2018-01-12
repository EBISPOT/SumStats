"""
Utils useful for querying
"""

from sumstats.snp.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def get_dsets_from_group(group, start, size):
    return gu.load_dsets_from_group(group=group, dset_names=TO_QUERY_DSETS, start=start, size=size)
