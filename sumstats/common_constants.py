import h5py

SNP_DSET = 'variant_id'
MANTISSA_DSET = 'mantissa'
EXP_DSET = 'exponent'
PVAL_DSET = 'pvalue'
STUDY_DSET = 'study_id'
CHR_DSET = 'chromosome'
BP_DSET = 'position'
OR_DSET = 'odds_ratio'
RANGE_U_DSET = 'ci_upper'
RANGE_L_DSET = 'ci_lower'
BETA_DSET = 'beta'
SE_DSET = 'standard_error'
EFFECT_DSET = 'effect_allele'
OTHER_DSET = 'other_allele'
FREQ_DSET = 'maf'
RSID_DSET = 'rsid'
MUTATION_DSET = 'type'
AC_DSET = 'ac'
AN_DSET = 'an'
HM_OR_DSET = 'hm_odds_ratio'
HM_RANGE_U_DSET = 'hm_ci_upper'
HM_RANGE_L_DSET = 'hm_ci_lower'
HM_BETA_DSET = 'hm_beta'
HM_EFFECT_DSET = 'hm_effect_allele'
HM_OTHER_DSET = 'hm_other_allele'
HM_FREQ_DSET = 'hm_effect_allele_frequency'
HM_VAR_ID = 'hm_variant_id'
HM_CODE = 'hm_code'


vlen_dtype = h5py.special_dtype(vlen=str)
DSET_TYPES = {SNP_DSET: vlen_dtype, RSID_DSET: vlen_dtype, MUTATION_DSET: vlen_dtype, AC_DSET: int, AN_DSET: int, PVAL_DSET: vlen_dtype, MANTISSA_DSET: float, EXP_DSET: int, STUDY_DSET: vlen_dtype,
              CHR_DSET: int, BP_DSET: int, OR_DSET: float, RANGE_U_DSET: float, RANGE_L_DSET: float, BETA_DSET: float, SE_DSET: float,
              EFFECT_DSET: vlen_dtype, OTHER_DSET: vlen_dtype, FREQ_DSET: float}
              

REFERENCE_DSET = MANTISSA_DSET
HARMONISATION_PREFIX = 'hm_'
GWAS_CATALOG_STUDY_PREFIX = 'GCST'

TO_DISPLAY_DEFAULT = {SNP_DSET, PVAL_DSET, STUDY_DSET, CHR_DSET, BP_DSET, EFFECT_DSET, OTHER_DSET, BETA_DSET, RSID_DSET, MUTATION_DSET, AC_DSET, AN_DSET, FREQ_DSET}

TO_DISPLAY_RAW = {SNP_DSET, PVAL_DSET, STUDY_DSET, CHR_DSET, BP_DSET, BETA_DSET,
                  EFFECT_DSET, OTHER_DSET}


TO_LOAD_DSET_HEADERS_DEFAULT = {SNP_DSET, PVAL_DSET, CHR_DSET, BP_DSET, EFFECT_DSET, OTHER_DSET, BETA_DSET, RSID_DSET, MUTATION_DSET, AC_DSET, AN_DSET, FREQ_DSET}
TO_STORE_DSETS_DEFAULT = {SNP_DSET, MANTISSA_DSET, EXP_DSET, STUDY_DSET, CHR_DSET, BP_DSET, EFFECT_DSET, OTHER_DSET, BETA_DSET, RSID_DSET, MUTATION_DSET, AC_DSET, AN_DSET, FREQ_DSET}
TO_QUERY_DSETS_DEFAULT = {SNP_DSET, MANTISSA_DSET, EXP_DSET, STUDY_DSET, CHR_DSET, BP_DSET, BETA_DSET, RSID_DSET, MUTATION_DSET, AC_DSET, AN_DSET, FREQ_DSET,
                  EFFECT_DSET, OTHER_DSET}
