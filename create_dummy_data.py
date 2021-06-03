from tests.prep_tests import *
import argparse
import snakemake

SINGLE_TRAIT = 'EFO_234567'
SMALL_PVALUE_DATA_DICT = DEFAULT_TEST_DATA_DICT.copy()
SMALL_PVALUE_DATA_DICT['p_value'] = ['0.3936E-200', 0.00000000000001, 0.0000000057479999999999996, '0.29600000000000004e-100', '0.7579E-123', 0.0000009358, 0.00000003662, 0.000009558, 0.000008675]
TEST_METADATA = [{'data_dict': DEFAULT_TEST_DATA_DICT, 'pmid': '123457', 'gcst': 'GCST123457', 'efo': DEFAULT_TEST_EFO},
                 {'data_dict': SMALL_PVALUE_DATA_DICT, 'pmid': '123458', 'gcst': 'GCST123458', 'efo': SINGLE_TRAIT}]

def create_dummy_data():
    conf = get_load_config()
    remove_loaded_data()
    prepare_load_env_with_test_data(conf)
    for item in TEST_METADATA:
        create_tsv_from_test_data_dict(test_data_dict=item['data_dict'], pmid=item['pmid'], gcst=item['gcst'], efo=item['efo'])
    # add in default test metadata
    TEST_METADATA.append({'pmid': DEFAULT_TEST_PMID, 'gcst': DEFAULT_TEST_GCST, 'efo': DEFAULT_TEST_EFO})
    snakemake.snakemake('Snakefile', config=conf, quiet=True)


def remove_dummy_data():
    remove_loaded_data()

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-mode", help='Create or clean dummy data', required=True, choices=['create', 'clean'], default='craete')
    args = argparser.parse_args()

    mode = args.mode
    if mode == 'create':
        create_dummy_data()
    elif mode == 'clean':
        remove_dummy_data()
    else:
        pass


if __name__ == '__main__':
    main()