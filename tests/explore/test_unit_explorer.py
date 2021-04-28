from sumstats.errors.error_classes import *
from sumstats.common_constants import *
import sumstats.explorer as ex
import pytest
from tests.prep_tests import create_tsv_from_test_data_dict, get_load_config, prepare_load_env_with_test_data, remove_loaded_data
from tests.test_constants import DEFAULT_TEST_DATA_DICT, DEFAULT_TEST_PMID, DEFAULT_TEST_GCST, DEFAULT_TEST_EFO
import snakemake

SPECIFIC_TRAIT = 'EFO_234567'
TEST_METADATA = [{'pmid': '123457', 'gcst': 'GCST123457', 'efo': DEFAULT_TEST_EFO},
                 {'pmid': '123458', 'gcst': 'GCST123458', 'efo': SPECIFIC_TRAIT}]

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


class TestLoader(object):
    def setup_method(self):
        self.explorer = ex.Explorer()
        self.loaded_traits = sorted(list(set([item['efo'] for item in TEST_METADATA])))
        self.loaded_studies = sorted(list(set([item['gcst'] for item in TEST_METADATA])))

    def test_get_list_of_traits(self):
        explored_list_of_traits = self.explorer.get_list_of_traits()
        assert len(explored_list_of_traits) == len(self.loaded_traits)
        for trait in self.loaded_traits:
            assert trait in explored_list_of_traits

    def test_get_list_of_studies_for_default_trait(self):
        list_of_studies_for_trait = self.explorer.get_list_of_studies_for_trait(DEFAULT_TEST_EFO)
        studies_for_trait = [item['gcst'] for item in TEST_METADATA if item['efo'] == DEFAULT_TEST_EFO]
        assert len(list_of_studies_for_trait) == len(studies_for_trait)
        for study in studies_for_trait:
            assert study in list_of_studies_for_trait

    def test_get_list_of_studies_for_specific_trait(self):
        list_of_studies_for_trait = self.explorer.get_list_of_studies_for_trait(SPECIFIC_TRAIT)
        studies_for_trait = [item['gcst'] for item in TEST_METADATA if item['efo'] == SPECIFIC_TRAIT]
        assert len(list_of_studies_for_trait) == len(studies_for_trait)
        for study in studies_for_trait:
            assert study in list_of_studies_for_trait

    def test_get_list_of_studies_for_non_existing_trait_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.get_list_of_studies_for_trait('t4')

    def test_get_list_of_studies(self):
        list_of_studies = self.explorer.get_list_of_studies()
        assert len(list_of_studies) == len(self.loaded_studies)
        for study in self.loaded_studies:
            assert study in list_of_studies

    def test_get_info_from_default_study(self):
        traits = self.explorer.get_trait_of_study(DEFAULT_TEST_GCST)
        for trait in traits:
            assert trait == DEFAULT_TEST_EFO

    def test_get_info_from_non_exising_study_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.get_trait_of_study('s6')

    def test_traits_return_in_same_order(self):
        traits1 = self.explorer.get_list_of_traits()
        traits2 = self.explorer.get_list_of_traits()
        for i in range(len(traits1)):
            assert traits1[i] == traits2[i]

    def test_studies_return_in_same_order(self):
        studies = self.explorer.get_list_of_studies_for_trait(DEFAULT_TEST_EFO)
        studies_for_trait = sorted(list(set([item['gcst'] for item in TEST_METADATA if item['efo'] == DEFAULT_TEST_EFO])))
        assert studies == studies_for_trait

    def test_trait_exists(self):
        for trait in self.loaded_traits:
            assert self.explorer.has_trait(trait)

    def test_trait_doesnt_exist_raises_error(self):
        with pytest.raises(NotFoundError):
            assert not self.explorer.has_trait('foo')

    def test_chromosome_exists(self):
        loaded_chrom = DEFAULT_TEST_DATA_DICT[CHR_DSET][0]
        assert self.explorer.has_chromosome(loaded_chrom)

    def test_chromosome_doesnt_exist_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.has_chromosome(3)