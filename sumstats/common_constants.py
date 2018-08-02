import h5py

SNP_DSET = 'variant_id'
MANTISSA_DSET = 'mantissa'
EXP_DSET = 'exponent'
PVAL_DSET = 'p_value'
STUDY_DSET = 'study_accession'
CHR_DSET = 'chromosome'
BP_DSET = 'base_pair_location'
OR_DSET = 'odds_ratio'
RANGE_DSET = 'confidence_interval'
BETA_DSET = 'beta'
SE_DSET = 'standard_error'
EFFECT_DSET = 'effect_allele'
OTHER_DSET = 'other_allele'
FREQ_DSET = 'effect_allele_frequency'
HM_OR_DSET = 'hm_odds_ratio'
HM_RANGE_DSET = 'hm_confidence_interval'
HM_BETA_DSET = 'hm_beta'
HM_EFFECT_DSET = 'hm_effect_allele'
HM_OTHER_DSET = 'hm_other_allele'
HM_FREQ_DSET = 'hm_effect_allele_frequency'
HM_VAR_ID = 'hm_variant_id'
HM_CODE = 'hm_code'


vlen_dtype = h5py.special_dtype(vlen=str)
DSET_TYPES = {SNP_DSET: vlen_dtype, PVAL_DSET: vlen_dtype, MANTISSA_DSET: float, EXP_DSET: int, STUDY_DSET: vlen_dtype,
              CHR_DSET: int, BP_DSET: int, OR_DSET: float, RANGE_DSET: vlen_dtype, BETA_DSET: float, SE_DSET: float,
              EFFECT_DSET: vlen_dtype, OTHER_DSET: vlen_dtype, FREQ_DSET: float, HM_EFFECT_DSET: vlen_dtype,
              HM_OTHER_DSET: vlen_dtype, HM_BETA_DSET: float, HM_OR_DSET: float, HM_FREQ_DSET: float, HM_CODE: int,
              HM_VAR_ID: vlen_dtype, HM_RANGE_DSET: vlen_dtype}

REFERENCE_DSET = MANTISSA_DSET
HARMONISATION_PREFIX = 'hm_'

TO_DISPLAY_DEFAULT = {SNP_DSET, PVAL_DSET, STUDY_DSET, CHR_DSET, BP_DSET, HM_OR_DSET, HM_RANGE_DSET,
                      HM_BETA_DSET, HM_EFFECT_DSET, HM_OTHER_DSET, HM_FREQ_DSET, HM_CODE}

TO_DISPLAY_RAW = {SNP_DSET, PVAL_DSET, STUDY_DSET, CHR_DSET, BP_DSET, OR_DSET, RANGE_DSET, BETA_DSET,
                  SE_DSET, EFFECT_DSET, OTHER_DSET, FREQ_DSET}


TO_LOAD_DSET_HEADERS_DEFAULT = {SNP_DSET, PVAL_DSET, CHR_DSET, BP_DSET, OR_DSET, RANGE_DSET, BETA_DSET,
                        SE_DSET, EFFECT_DSET, OTHER_DSET, FREQ_DSET, HM_OR_DSET, HM_RANGE_DSET, HM_BETA_DSET,
                                HM_EFFECT_DSET, HM_OTHER_DSET, HM_FREQ_DSET, HM_VAR_ID, HM_CODE}
TO_STORE_DSETS_DEFAULT = {SNP_DSET, MANTISSA_DSET, EXP_DSET, STUDY_DSET, CHR_DSET, BP_DSET, OR_DSET, RANGE_DSET,
                  BETA_DSET, SE_DSET, EFFECT_DSET, OTHER_DSET, FREQ_DSET, HM_OR_DSET, HM_RANGE_DSET, HM_BETA_DSET,
                                HM_EFFECT_DSET, HM_OTHER_DSET, HM_FREQ_DSET, HM_VAR_ID, HM_CODE}
TO_QUERY_DSETS_DEFAULT = {SNP_DSET, MANTISSA_DSET, EXP_DSET, STUDY_DSET, CHR_DSET, BP_DSET, OR_DSET, RANGE_DSET, BETA_DSET,
                  SE_DSET, EFFECT_DSET, OTHER_DSET, FREQ_DSET, HM_OR_DSET, HM_RANGE_DSET, HM_BETA_DSET,
                                HM_EFFECT_DSET, HM_OTHER_DSET, HM_FREQ_DSET, HM_VAR_ID, HM_CODE}
