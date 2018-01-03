"""
Utils useful for querying
"""

from sumstats.snp.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def get_dsets_from_group(group, start, size):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    return gu.extend_dsets_for_group(group=group, name_to_dataset=name_to_dataset, start=start, size=size)
