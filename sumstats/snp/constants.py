"""
When storing datasets by SNP we do not need a dataset for storing the variant id.
as the dataset will be stored under the group that will be named after the variant id.

Stored as /SNP/DATA
    Where DATA:
    under each directory we store 3 (or more) vectors
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'bp' list will hold the baise pair location that each snp belongs to
    e.t.c.
"""

from sumstats.common_constants import *

TO_LOAD_DSET_HEADERS = TO_LOAD_DSET_HEADERS_DEFAULT.copy()

TO_STORE_DSETS = TO_STORE_DSETS_DEFAULT.copy()
TO_STORE_DSETS.remove(SNP_DSET)

TO_QUERY_DSETS = TO_STORE_DSETS_DEFAULT.copy()
TO_QUERY_DSETS.remove(SNP_DSET)
