from tests.test_constants import *
import sumstats.utils.group as gu


def prepare_dictionary():
    return {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
            "effect": effectarray, "other": otherarray, 'freq': frequencyarray}


def prepare_load_object_with_study(h5file, study, loader):
    loader_dictionary = prepare_dictionary()
    return loader.Loader(None, h5file, study, loader_dictionary)


def prepare_load_object_with_study_and_trait(h5file, study, trait, loader):
    loader_dictionary = prepare_dictionary()
    return loader.Loader(None, h5file, study, trait, loader_dictionary)


def save_snps_and_study_in_file(opened_file, list_of_snps, study):
    for snp in list_of_snps:
        group = opened_file.create_group(snp)
        gu.create_dataset(group, 'study', [study])