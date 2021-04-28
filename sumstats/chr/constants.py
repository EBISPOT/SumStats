"""
When storing datasets by chromosome we do not need a dataset for storing the chromosome.
as the dataset will be stored under the group that will be named after the chromosome.

Stored as /CHR/BLOCK/DATA
    Where DATA:
    under each BLOCK directory we store 3 (or more) vectors
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    e.t.c.
"""

from sumstats.common_constants import *

TO_LOAD_DSET_HEADERS = TO_LOAD_DSET_HEADERS_DEFAULT.copy()

TO_STORE_DSETS = TO_STORE_DSETS_DEFAULT.copy()

TO_QUERY_DSETS = TO_LOAD_DSET_HEADERS_DEFAULT.copy()