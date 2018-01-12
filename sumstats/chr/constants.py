from sumstats.common_constants import *

TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr', 'or', 'bp', 'effect', 'other', 'freq']
TO_STORE_DSETS = ['snp', 'mantissa', 'exp', 'or', 'study', 'bp', 'effect', 'other', 'freq']
TO_QUERY_DSETS = ['snp', 'mantissa', 'exp', 'or', 'study', 'bp', 'effect', 'other', 'freq']

BLOCK_SIZE = 100000

REFERENCE_DSET = MANTISSA_DSET