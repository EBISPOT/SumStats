"""
When storing datasets by trait we do not need a dataset for storing the study accessions
as the dataset will be stored under the group that will be named after the study accession.

Data is stored in the hierarchy of /Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    'snp' list will hold the variant ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'chr' list will hold the chromosome that each snp belongs to
    e.t.c.
"""

from sumstats.common_constants import *

TO_LOAD_DSET_HEADERS = TO_LOAD_DSET_HEADERS_DEFAULT.copy()

TO_STORE_DSETS = TO_STORE_DSETS_DEFAULT.copy()
TO_STORE_DSETS.remove(STUDY_DSET)

TO_QUERY_DSETS = TO_LOAD_DSET_HEADERS_DEFAULT.copy()