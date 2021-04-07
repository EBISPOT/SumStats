from tests.prep_tests import *
import snakemake
import pytest


@pytest.fixture(scope="session", autouse=True)
def prep():
    print("START")
    conf = get_load_config()
    prepare_load_env_with_test_data(conf)
    snakemake.snakemake('Snakefile', config=conf)
    yield
    remove_loaded_data()
    print("END")
