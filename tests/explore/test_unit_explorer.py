from sumstats.errors.error_classes import *
import sumstats.explorer as ex
import pytest
from tests.prep_tests import create_tsv_from_test_data_dict, get_load_config, prepare_load_env_with_test_data, remove_loaded_data
from tests.test_constants import GCST, EFO
import snakemake


test_metadata = [{'pmid': '123457', 'gcst': 'GCST123457', 'efo': EFO},
                 {'pmid': '123458', 'gcst': 'GCST123458', 'efo': 'EFO_234567'}]

@pytest.yield_fixture(scope="session", autouse=True)
def load_data():
    conf = get_load_config()
    prepare_load_env_with_test_data(conf)
    for item in test_metadata:
        create_tsv_from_test_data_dict(pmid=item['pmid'], gcst=item['gcst'], efo=item['efo'])
    snakemake.snakemake('Snakefile', config=conf)
    yield
    remove_loaded_data()


class TestLoader(object):
    def setup_method(self):
        self.explorer = ex.Explorer()
        loaded_traits = [item['efo'] for item in test_metadata]
        loaded_traits.append(EFO)
        self.loaded_traits = list(set(loaded_traits))

    def test_get_list_of_traits(self):
        explored_list_of_traits = self.explorer.get_list_of_traits()
        print(explored_list_of_traits)
        print(self.loaded_traits)
        assert len(explored_list_of_traits) == len(self.loaded_traits)
        for trait in self.loaded_traits:
            assert trait in explored_list_of_traits

    def test_get_list_of_studies_for_trait_t1(self):
        list_of_studies = self.explorer.get_list_of_studies_for_trait('t1')
        assert len(list_of_studies) == len(self.loaded_studies_t1)
        for study in self.loaded_studies_t1:
            assert study in list_of_studies

    def test_get_list_of_studies_for_trait_t3(self):
        list_of_studies = self.explorer.get_list_of_studies_for_trait('t3')
        assert len(list_of_studies) == len(self.loaded_studies_t3)
        for study in self.loaded_studies_t3:
            assert study in list_of_studies

    def test_get_list_of_studies_for_non_existing_trait_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.get_list_of_studies_for_trait('t4')

    def test_get_list_of_studies(self):
        list_of_studies = self.explorer.get_list_of_studies()
        assert len(list_of_studies) == len(self.loaded_studies)
        for study in self.loaded_studies:
            assert study in list_of_studies

    def test_get_info_from_study_s1(self):
        trait = self.explorer.get_trait_of_study('s1')
        assert trait == 't1'

    def test_get_info_from_non_exising_study_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.get_trait_of_study('s6')

    def test_traits_return_in_same_order(self):
        traits1 = self.explorer.get_list_of_traits()
        traits2 = self.explorer.get_list_of_traits()
        for i in range(len(traits1)):
            assert traits1[i] == traits2[i]

    def test_studies_return_in_same_order(self):
        studies1 = self.explorer.get_list_of_studies_for_trait('t1')
        studies2 = self.explorer.get_list_of_studies_for_trait('t1')
        for i in range(len(studies1)):
            assert studies1[i] == studies2[i]

    def test_trait_exists(self):
        for trait in self.loaded_traits:
            assert self.explorer.has_trait(trait)

    def test_trait_doesnt_exist_raises_error(self):
        with pytest.raises(NotFoundError):
            assert not self.explorer.has_trait('foo')

    def test_chromosome_exists(self):
        assert self.explorer.has_chromosome(1)

    def test_chromosome_doesnt_exist_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.has_chromosome(3)