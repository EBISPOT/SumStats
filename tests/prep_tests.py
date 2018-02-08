from tests.test_constants import *
import sumstats.utils.group as gu


def prepare_dictionary(test_arrays=None):
    if test_arrays is None:
        return {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
    else:
        return {"snp": test_arrays.snpsarray, "pval": test_arrays.pvalsarray, "chr": test_arrays.chrarray, "or": test_arrays.orarray, "bp": test_arrays.bparray,
                "effect": test_arrays.effectarray, "other": test_arrays.otherarray, 'freq': test_arrays.frequencyarray}


def prepare_load_object_with_study(h5file, study, loader):
    loader_dictionary = prepare_dictionary()
    return loader.Loader(None, h5file, study, loader_dictionary)


def prepare_load_object_with_study_and_trait(h5file, study, loader, test_arrays=None, trait=None):
    loader_dictionary = prepare_dictionary(test_arrays)
    if trait is not None:
        return loader.Loader(None, h5file, study, trait, loader_dictionary)
    else:
        return loader.Loader(None, h5file, study, loader_dictionary)


def save_snps_and_study_in_file(opened_file, list_of_snps, study):
    for snp in list_of_snps:
        group = gu.Group(opened_file.create_group(snp))
        group.generate_dataset('study', [study])
