import h5py

TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr', 'or', 'bp', 'effect', 'other', 'freq']
TO_STORE_DSETS = ['snp', 'mantissa', 'exp', 'chr', 'or', 'bp', 'effect', 'other', 'freq']
TO_QUERY_DSETS = ['snp', 'mantissa', 'exp', 'chr', 'or', 'study', 'bp', 'effect', 'other', 'freq']

vlen_dtype = h5py.special_dtype(vlen=str)
DSET_TYPES = {'snp' : vlen_dtype, 'pval' : vlen_dtype, 'mantissa': float, 'exp': int,
              'chr': int, 'or' : float, 'bp' : int, 'effect' : vlen_dtype, 'other' : vlen_dtype, 'freq': float}
# DSET_TYPES = {'snp' : vlen_dtype, 'mantissa': float, 'exp': int,
#               'chr': int, 'or' : float, 'bp' : int, 'effect' : vlen_dtype, 'other' : vlen_dtype, 'freq': float}

SNP_DSET = 'snp'
BP_DSET = 'bp'
PVAL_DSET = 'pval'
MANTISSA_DSET = 'mantissa'
EXP_DSET = 'exp'
CHR_DSET = 'chr'
STUDY_DSET = 'study'
REFERENCE_DSET = MANTISSA_DSET