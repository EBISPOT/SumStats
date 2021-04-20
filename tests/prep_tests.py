from tests.test_constants import DEFAULT_TEST_DATA_DICT, DEFAULT_TEST_PMID, DEFAULT_TEST_GCST, DEFAULT_TEST_EFO
import pandas as pd
import yaml
import pathlib
import os


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
        snp_study = "/".join([snp, study])
        group = gu.Group(opened_file.create_group(snp_study))
        group.generate_dataset(STUDY_DSET, [study])

def get_load_config():
    with open("tests/test_snakemake_config.yaml") as f:
        conf = yaml.safe_load(f)
        return conf

def create_tsv_from_test_data_dict(test_data_dict=DEFAULT_TEST_DATA_DICT, conf=get_load_config(), pmid=DEFAULT_TEST_PMID, gcst=DEFAULT_TEST_GCST, efo=DEFAULT_TEST_EFO):
    sumstats_filename = '-'.join([pmid, gcst, efo]) + '.tsv'
    sumstats_file_path = os.path.join(conf['to_load'], sumstats_filename)
    df = pd.DataFrame.from_dict(test_data_dict)
    df.to_csv(sumstats_file_path, sep='\t', index=False)

def prepare_load_env_with_test_data(conf):
    # create dirs
    pathlib.Path(conf['loaded']).mkdir(parents=True, exist_ok=True)
    pathlib.Path(conf['to_load']).mkdir(parents=True, exist_ok=True)
    pathlib.Path(conf['out_dir']).mkdir(parents=True, exist_ok=True)
    create_tsv_from_test_data_dict(test_data_dict=DEFAULT_TEST_DATA_DICT, conf=conf)

def remove_loaded_data():
    snakemake_conf_dict = get_load_config()
    rmdir(snakemake_conf_dict['loaded'])
    rmdir(snakemake_conf_dict['to_load'])
    rmdir(snakemake_conf_dict['out_dir'])

def rmdir(directory):
    directory = pathlib.Path(directory)
    if directory.exists():
        for item in directory.iterdir():
            if item.is_dir():
                rmdir(item)
            else:
                item.unlink()
        directory.rmdir()
    else:
        pass







