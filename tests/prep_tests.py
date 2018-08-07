from tests.test_constants import *
import sumstats.utils.group as gu


def prepare_dictionary(test_arrays=None):
    if test_arrays is None:
        return {SNP_DSET: snpsarray, PVAL_DSET: pvalsarray, CHR_DSET: chrarray, OR_DSET: orarray, BP_DSET: bparray,
                EFFECT_DSET: effectarray, OTHER_DSET: otherarray, FREQ_DSET: frequencyarray, SE_DSET: searray, BETA_DSET: betaarray,
                RANGE_L_DSET: rangearray, RANGE_U_DSET: rangearray, HM_OR_DSET: orarray, HM_RANGE_L_DSET: rangearray, HM_RANGE_U_DSET: rangearray,
                HM_BETA_DSET: betaarray, HM_EFFECT_DSET: effectarray, HM_OTHER_DSET: otherarray, HM_FREQ_DSET: frequencyarray,
                HM_VAR_ID: snpsarray, HM_CODE: codearray}
    else:
        return {SNP_DSET: test_arrays.snpsarray, PVAL_DSET: test_arrays.pvalsarray, CHR_DSET: test_arrays.chrarray,
                OR_DSET: test_arrays.orarray, BP_DSET: test_arrays.bparray,
                EFFECT_DSET: test_arrays.effectarray, OTHER_DSET: test_arrays.otherarray, FREQ_DSET: test_arrays.frequencyarray,
                SE_DSET: test_arrays.searray, BETA_DSET: test_arrays.betaarray, RANGE_L_DSET: test_arrays.rangearray, RANGE_U_DSET: test_arrays.rangearray,
                HM_OR_DSET: test_arrays.orarray,HM_RANGE_L_DSET: test_arrays.rangearray, HM_RANGE_U_DSET: test_arrays.rangearray, HM_BETA_DSET: test_arrays.betaarray,
                HM_EFFECT_DSET: test_arrays.effectarray, HM_OTHER_DSET: test_arrays.otherarray, HM_FREQ_DSET: test_arrays.frequencyarray,
                HM_VAR_ID: test_arrays.snpsarray, HM_CODE: test_arrays.codearray}


def prepare_load_object_with_study(h5file, study, loader, test_arrays=None):
    loader_dictionary = prepare_dictionary(test_arrays)
    return loader.Loader(None, h5file, study, loader_dictionary)


def prepare_load_object_with_study_and_trait(h5file, study, loader, trait, test_arrays=None):
    loader_dictionary = prepare_dictionary(test_arrays)
    return loader.Loader(None, h5file, study, trait, loader_dictionary)


def save_snps_and_study_in_file(opened_file, list_of_snps, study):
    for snp in list_of_snps:
        group = gu.Group(opened_file.create_group(snp))
        group.generate_dataset(STUDY_DSET, [study])
