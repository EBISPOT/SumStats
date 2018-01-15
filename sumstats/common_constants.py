import h5py

vlen_dtype = h5py.special_dtype(vlen=str)
DSET_TYPES = {'snp' : vlen_dtype, 'pval' : vlen_dtype, 'mantissa': float, 'exp': int, 'study' : vlen_dtype,
              'chr': int, 'or' : float, 'bp' : int, 'effect' : vlen_dtype, 'other' : vlen_dtype, 'freq': float}

SNP_DSET = 'snp'
BP_DSET = 'bp'
MANTISSA_DSET = 'mantissa'
EXP_DSET = 'exp'
PVAL_DSET = 'pval'
CHR_DSET = 'chr'
STUDY_DSET = 'study'
OR_DSET = 'or'
EFFECT_DSET = 'effect'
OTHER_DSET = 'other'
FREQ_DSET = 'freq'

REFERENCE_DSET = MANTISSA_DSET