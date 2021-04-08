from tests.prep_tests import *
import snakemake
import pytest


SINGLE_TRAIT = 'EFO_234567'
TEST_METADATA = [{'pmid': '123457', 'gcst': 'GCST123457', 'efo': DEFAULT_TEST_EFO},
                 {'pmid': '123458', 'gcst': 'GCST123458', 'efo': SINGLE_TRAIT}]

@pytest.yield_fixture(scope="session", autouse=True)
def load_data():
    conf = get_load_config()
    prepare_load_env_with_test_data(conf)
    for item in TEST_METADATA:
        create_tsv_from_test_data_dict(pmid=item['pmid'], gcst=item['gcst'], efo=item['efo'])
    # add in default test metadata
    TEST_METADATA.append({'pmid': DEFAULT_TEST_PMID, 'gcst': DEFAULT_TEST_GCST, 'efo': DEFAULT_TEST_EFO})
    snakemake.snakemake('Snakefile', config=conf)
    # here is where all the tests in this session run
    yield
    # then we tear it all down
    remove_loaded_data()